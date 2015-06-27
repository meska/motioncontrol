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

# Create your models here.
class Server(models.Model):
    name = models.CharField(max_length=100,unique=True)
    admin_url = models.CharField(max_length=200,unique=True,default='http://127.0.0.1:8000/')
    config_folder = models.CharField(max_length=200,null=True,blank=True)
    local_data_folder = models.CharField(max_length=200,null=True,blank=True)
    remote_data_folder = models.CharField(max_length=200,null=True,blank=True,help_text='Use if motion server on different system')
    
    
    #class Meta:
        #app_label = 'motioncontrol'

    
    def __unicode__(self):
        return self.name
    
    def getVal(self,name):
        try:   
            out = ""
            res = requests.get(urljoin(self.admin_url,'0/config/get?query=%s' % (name))).text.splitlines()[0:-1]
            for r in res:
                out+=r.split(' = ')[1]
                return out
        except Exception,e:
            import inspect
            logging.error("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))
        return ""
    
    def setVal(self,name,val):
        try:
            if not val == self.getVal(name).strip():
                r = requests.get(urljoin(self.admin_url,'0/config/set'),params={name:quote(val)})
                if r.text.splitlines()[-1] == 'Done':
                    r = requests.get(urljoin(self.admin_url,'0/config/writeyes'))
                
        except Exception,e:
            import inspect
            logging.error("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))
            return False
        
        return self.getVal(name)    
    
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
        self.setVal('output_pictures','off')
    
    @property  
    def cams(self):
        try:
            out = []
            res = requests.get(self.admin_url).text.splitlines()[2:]
            for r in res:
                c = Cam.objects.get_or_create(server=self,thread_number=int(r.strip()))[0]
                out.append(c)
                if not c.name:
                    c.save()

            return out
        except Exception,e:
            import inspect
            logging.error("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))
        return []    
    
    
class Cam(models.Model):
    server = models.ForeignKey(Server)
    name = models.CharField(max_length=100,null=True,blank=True)
    slug = models.CharField(max_length=100,null=True,blank=True)
    thread_number = models.IntegerField(null=True,blank=True)
    output_pictures = models.BooleanField(default=True)
    online = models.BooleanField(default=True)

    #class Meta:
    #    app_label = 'motioncontrol'

    
    def __unicode__(self):
        return self.name    
    
    def getVal(self,name):
        try:   
            out = ""
            res = requests.get('%s%s/config/get?query=%s' % (self.server.admin_url,self.thread_number,name)).text.splitlines()[0:-1]
            for r in res:
                out+=r.split(' = ')[1]
                return out
        except Exception,e:
            import inspect
            logging.error("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))
        return ""
    
    def setVal(self,name,val,restart=True):
        try:
            if not val == self.getVal(name).strip():
                res = requests.get(urljoin(self.server.admin_url,'/%s/config/set'%self.thread_number),params={name:val})
                if res.text.splitlines()[-1] == 'Done':
                    res = requests.get(urljoin(self.server.admin_url,'/%s/config/writeyes' % self.thread_number ))
                    if res.text.splitlines()[-1] == 'Done':
                        if restart:
                            res = requests.get(urljoin(self.server.admin_url,'/%s/action/restart' % self.thread_number))

        except Exception,e:
            import inspect
            logging.error("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))
            return False
        
        return self.getVal(name)

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
            #['on_motion_detected','/etc/motion/on_event.py motion '+ self.slug +' %Y%m%d %H%M%S'],
            ['target_dir',os.path.join(self.server.remote_data_folder,slugify(self.name))]
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
    lt = cam.getVal('text_left')
    if not cam.name == lt.strip():
        cam.name = lt.strip()
        cam.save()
        return

    if not cam.slug == slugify("%s %s" % (cam.name,cam.thread_number)):
        cam.slug = slugify("%s %s" % (cam.name,cam.thread_number))
        cam.save()
        return

    Thread(target=cam.checksettings).start()