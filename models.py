from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
import cStringIO,requests
from django.template.defaultfilters import slugify
from django.core.cache import cache
from django.conf import settings
from threading import Thread
from PIL import Image
from time import sleep
import redis
import logging,os,sys
import json
from urllib import quote
from urlparse import urljoin,urlsplit
#logger = logging.getLogger(__name__)




class Server(models.Model):
    name = models.CharField(max_length=100,unique=True)
    admin_url = models.CharField(max_length=200,unique=True,default='http://127.0.0.1:8000/')
    local_config_folder = models.CharField(max_length=200,null=True,blank=True,help_text='On motion server')
    local_data_folder = models.CharField(max_length=200,null=True,blank=True,help_text='On motion server')
    remote_config_folder = models.CharField(max_length=200,null=True,blank=True,help_text='On Django server')
    remote_data_folder = models.CharField(max_length=200,null=True,blank=True,help_text='On Django server')
    
    
    class Meta:
        managed=True
        #app_label = 'motioncontrol'

    
    def __unicode__(self):
        return self.name
    
    def getVal(self,thread_number,name):
        # get values from motioncontrol server with retry
        c = cache.get('motion-setting-%s-%s' % (thread_number,name))
        if c:
            return c 

        try:
            r = requests.get('%s%s/config/get' % (self.admin_url,thread_number),params={'query':name},timeout=30)
            if r.status_code == requests.codes.ok:
                # get only the first line atm
                val = r.text.splitlines()[0].split("=")[1].strip() 
                c = cache.set('motion-setting-%s-%s' % (thread_number,name),val,60)
                return val

        except Exception,e:
            import inspect
            logging.error("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))
        
        return None        

    
    def setVal(self,thread_number,name,val,restart=True):
        prev = self.getVal(thread_number, name)
        if not prev == None and not prev == val:
            # value differs, updating
            try:
                r = requests.get('%s%s/config/set' % (self.admin_url,thread_number),params={name:quote(val)},timeout=30)
                if r.status_code == requests.codes.ok:
                
                    r = requests.get('%s%s/config/writeyes' % (self.admin_url,thread_number),timeout=30)
                    if restart:
                        r = requests.get('%s%s/action/restart' % (self.admin_url,thread_number),timeout=30)
                    return val 
                
            except Exception,e:
                import inspect
                logging.error("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))
                
        return None
 
    
    def restart(self):
        try:
            res = requests.get(urljoin(self.server.admin_url,'/0/action/restart')) 
        except Exception,e:
            import inspect
            logging.error("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))
            return False

        return res
    
    def checkSettings(self):
        # set default server settings
        self.setVal('0','output_pictures','off')
    
    @property  
    def cams(self):
        out = []
        
        r = None
        for i in range(5):
            try:
                r = requests.get(self.admin_url,timeout=30)
                if r:
                    break
            except:
                sleep(5)

        if not r == None:
            if r.status_code == requests.codes.ok:
                res = r.text.splitlines()[2:]
    
                for r in res:
                    c,created = Cam.objects.get_or_create(server=self,thread_number=int(r.strip()))
                    if created:
                        c.checksettings()
                    if not c.name:
                        c.save()
                    out.append(c)
                return out
        return []    
    
    
class Cam(models.Model):
    server = models.ForeignKey(Server)
    name = models.CharField(max_length=100,null=True,blank=True)
    slug = models.CharField(max_length=100,null=True,blank=True)
    thread_number = models.IntegerField(null=True,blank=True)
    output_pictures = models.BooleanField(default=True)
    online = models.BooleanField(default=True)
    last_event = models.DateTimeField(null=True,blank=True)

    class Meta:
        managed=True
    #    app_label = 'motioncontrol'

    
    def __unicode__(self):
        return self.name    
    
    def getVal(self,name):
        return self.server.getVal(self.thread_number,name)
    
    def setVal(self,name,val,restart=True):
        return self.server.setVal(self.thread_number,name,val,restart)

    def restart(self):
        try:
            res = requests.get(urljoin(self.server.admin_url,'/%s/action/restart' % self.thread_number))
        except Exception,e:
            import inspect
            logging.error("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))
            return False
        
        return res

    def checksettings(self):
        default_settings = [
            ['stream_port',"%s%03d"  % (48,int(self.thread_number))],
            ['stream_localhost',"off"],
            ['stream_motion',"on"],
            ['netcam_tolerant_check',"on"],
            ['netcam_keepalive',"off"],
            ['threshold',"1500"],
            ['threshold_tune',"on"],
            ['minimum_motion_frames',"3"],
            ['ffmpeg_timelapse',"5"],
            ['ffmpeg_timelapse_mode',"daily"],
            ['output_pictures',"best" if self.output_pictures else "off"],
            ['on_picture_save','/etc/motion/on_event.py picture '+ self.slug +' %Y%m%d %H%M%S %v %t %f'],
            ['on_camera_lost','/etc/motion/on_event.py lost '+ self.slug +' %Y%m%d %H%M%S'],
            ['on_motion_detected','/etc/motion/on_event.py motion '+ self.slug +' %Y%m%d %H%M%S'],
            ['target_dir',os.path.join(self.server.local_data_folder,slugify(self.name))]
            ]
        
        for e in default_settings:
            try:
                if not self.getVal(e[0]).strip() == e[1]:
                    logging.info('Updated %s --> %s' % (e[0],e[1]))
                    self.setVal(e[0],e[1],False)
            except:
                logging.error('Error Updating  %s --> %s' % (e[0],e[1]))
        
        self.restart()

    def snapshot(self):

        port = self.getVal('stream_port').strip()
        if not port:
            img = Image.open(os.path.join(os.path.split(__file__)[0],'static','disconnected.jpg')).resize([640,480])
            return img 
        
        streamurl = "http://%s:%s/" % (urlsplit(self.server.admin_url).hostname,port)     
        
        try:
            # get jpeg from mjpeg stream
            r = requests.get(streamurl,stream=True)
            data=''
            for chunk in r.iter_content(chunk_size=1024):
                data+=chunk
                a = data.find('\xff\xd8')
                b = data.find('\xff\xd9')                
                if a!=-1 and b!=-1:
                    jpg = data[a:b+2]
                    img = Image.open(cStringIO.StringIO(jpg)).resize([640,480])
                    return img                
        
        except Exception,e:
            import inspect
            logging.error("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))

            img = Image.open(os.path.join(os.path.split(__file__)[0],'static','disconnected.jpg')).resize([640,480])
            return img
        
    def streamurl(self):
        if self.getVal('stream_port'):
            port = self.getVal('stream_port').strip()
            if not int(port):
                self.save()
            return "http://%s:%s/" % (urlsplit(self.server.admin_url).hostname,port) 
        else:
            # return disconnected url
            return None   

    def last_events(self):
        return self.event_set.all().order_by('-datetime')[0:20]
        
class ConfigValue(models.Model):
    cam = models.ForeignKey(Cam)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    
    
    #class Meta:
    #    app_label = 'motioncontrol'
    
    def __unicode__(self):
        return self.name    
    
class Event(models.Model):
    """
     Table update from motion server
    """
    cam = models.ForeignKey(Cam)
    datetime = models.DateTimeField()
    event_type = models.IntegerField()
    filename = models.CharField(max_length=250)

    class Meta:
        #app_label = 'motioncontrol'
        unique_together = (("cam", "filename"),)

    def img(self):
        try:
            filename = os.path.join(
                self.cam.server.local_data_folder,
                os.path.split(self.cam.getVal('target_dir').strip())[1]
                ,self.filename
                )
            if os.path.exists(filename):
                img = Image.open(filename).resize([320,200]) 
                return img
            else:
                return None
        except Exception,e:
            import inspect
            logging.error("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))
            return None
        
@receiver(post_save, sender=Server)
def post_save_server(sender, **kwargs):
    srv = kwargs.get('instance')
    logging.info("POST_SAVE : ConfigValue : %s" % srv)
    # previous
    Thread(target=srv.checkSettings).start()
    
    
@receiver(post_save, sender=Cam)
def post_save_cam(sender, **kwargs):
    cam = kwargs.get('instance')
    logging.info("POST_SAVE : Job : %s" % cam.thread_number)
    # check number
    if not cam.name:
        lt = cam.getVal('text_left')
        if lt and not cam.name == lt:
            cam.name = lt
            cam.save()
            return

    if not cam.slug == slugify("%s %s" % (cam.name,cam.thread_number)):
        cam.slug = slugify("%s %s" % (cam.name,cam.thread_number))
        cam.save()
        return

    #Thread(target=cam.checksettings).start()