from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from io import BytesIO
import requests
from django.template.defaultfilters import slugify
from django.core.cache import cache
from django.conf import settings
from threading import Thread
from PIL import Image
from time import sleep
import logging,os
import re
#logger = logging.getLogger(__name__)




class Server(models.Model):
    name = models.CharField(max_length=100,unique=True)
    admin_url = models.CharField(max_length=200,unique=True,default='http://127.0.0.1:8000/')
    stream_url = models.CharField(max_length=200,unique=True,default='http://127.0.0.1/',help_text='Stream base url, requires nginx configuration')
    local_config_folder = models.CharField(max_length=200,null=True,blank=True,help_text='On motion server')
    local_data_folder = models.CharField(max_length=200,null=True,blank=True,help_text='On motion server')
    remote_config_folder = models.CharField(max_length=200,null=True,blank=True,help_text='On Django server')
    remote_data_folder = models.CharField(max_length=200,null=True,blank=True,help_text='On Django server')
    
    
    class Meta:
        managed=True
        #app_label = 'motioncontrol'

    
    def __unicode__(self):
        return self.name
    
    def getVal(self,thread_number,name,cached=True):
        # get values from motioncontrol server with retry
        c = cache.get('motion-setting-%s-%s' % (thread_number,name))
        if c and cached:
            return c 

        try:
            r = requests.get('%s%s/config/get' % (self.admin_url,thread_number),params={'query':name},timeout=30)
            if r.status_code == requests.codes.ok:
                # get only the first line atm
                val = r.text.splitlines()[0].split("=")[1].strip() 
                c = cache.set('motion-setting-%s-%s' % (thread_number,name),val,600)
                return val
            else:
                import inspect
                print("%s:%s:%s" % (inspect.currentframe().f_back.f_code.co_name,name,r))

        except Exception as e:
            import inspect
            print("%s:%s:%s" % (inspect.currentframe().f_back.f_code.co_name,name,e))
        
        return None        

    
    def setVal(self,thread_number,name,val,restart=True,cached=True):
        prev = self.getVal(thread_number, name,cached)
        if not prev == None and not prev == val:
            # value differs, updating
            try:
                r = requests.get('%s%s/config/set' % (self.admin_url,thread_number),params={name:val},timeout=30)
                if r.status_code == requests.codes.ok:
                
                    r = requests.get('%s%s/config/write' % (self.admin_url,thread_number),timeout=30)
                    sleep(1)
                    if restart:
                        r = requests.get('%s%s/action/restart' % (self.admin_url,thread_number),timeout=30)
                    return val 
                
            except Exception as e:
                import inspect
                print("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))
                
        return None
 
    
    def restart(self):
        try:
            res = requests.get(self.admin_url + '0/action/restart') 
        except Exception as e:
            import inspect
            print("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))
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
    on_event_script = models.CharField(max_length=200,default='/etc/motion/on_event_webhook.py')
    

    class Meta:
        managed=True
    #    app_label = 'motioncontrol'

    def __str__(self):
        return "%s@%s" % (self.name,self.server.name)

    def __unicode__(self):
        return u"%s@%s" % (self.name,self.server.name)
    
    @property
    def is_online(self):
        try:
            r = requests.get('%s%s/detection/connection' % (self.server.admin_url,self.thread_number))
        except Exception as e:
            # return last value on error
            return self.online
        
        if r.status_code == requests.codes.ok:
            ok = True if 'OK' in r.text else False
            if not self.online == ok:
                self.online = ok
                self.save()
            return ok
        else:
            return self.online
    
    def getVal(self,name,cached=True):
        return self.server.getVal(self.thread_number,name,cached)
    
    def setVal(self,name,val,restart=True,cached=True):
        return self.server.setVal(self.thread_number,name,val,restart,cached)
    
    def restart(self):
        try:
            res = requests.get('%s/%s/action/restart' % (self.server.admin_url,self.thread_number))
        except Exception as e:
            import inspect
            print("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))
            return False
        
        return res

    def checksettings(self):
        
        default_settings = [
            ['stream_port',"%s%03d"  % (48,int(self.thread_number))],
            ['stream_localhost',"off"],
            ['stream_motion',"on"],
            ['netcam_tolerant_check',"on"],
            ['netcam_keepalive',"off"],
            ['width',"640"],
            ['height',"480"],
            #['threshold',"1500"],
            #['threshold_tune',"on"],
            ['minimum_motion_frames',"3"],
            ['ffmpeg_timelapse',"5"],
            ['ffmpeg_timelapse_mode',"daily"],
            ['output_pictures',"best" if self.output_pictures else "off"],
            ['on_picture_save',self.on_event_script + ' picture '+ self.slug +' %Y%m%d %H%M%S %v %t %f'],
            #['on_camera_lost',self.on_event_script + ' lost '+ self.slug +' %Y%m%d %H%M%S'],
            #['on_motion_detected',self.on_event_script + ' motion '+ self.slug +' %Y%m%d %H%M%S'],
            ['noise_level','32'],
            ['noise_tune','on'],          
            ['threshold','1500'],
            ['threshold_tune','on'],   
            ['on_camera_lost',''],
            ['on_motion_detected',''],            
            ['target_dir',os.path.join(self.server.local_data_folder,slugify(self.name))]
            ]
        
        # if pause alert enabled
        #if self.alertsubscription_set.filter(alert_nomotion=True,enabled=True).count() > 0:
            #default_settings.append(['threshold','100'])
            #default_settings.append(['threshold_tune','off'])
            
        
        for e in default_settings:
            try:
                if not self.getVal(e[0]).strip() == e[1]:
                    logging.info('Updated %s --> %s' % (e[0],e[1]))
                    self.setVal(e[0],e[1],False)
            except:
                print('Error Updating  %s --> %s' % (e[0],e[1]))
        
        self.restart()

    def snapshot(self):
        c = cache.get('snap-%s-%s' % (self.server.id,self.id))
        if c:
            return c 
        
        port = self.getVal('stream_port')
        if not port:
            img = Image.open(os.path.join(os.path.split(__file__)[0],'static','disconnected.jpg')).resize([640,480])
            return img 
        
        if re.findall(':\d+',self.server.admin_url):
            streamurl = re.sub(':\d+',':'+port,self.server.admin_url)
        else:
            streamurl = "%s:%s/" % (self.server.admin_url[0:-1],port)
            
        
        try:
            # get jpeg from mjpeg stream
            r = requests.get(streamurl,stream=True)
            data=b''
            for chunk in r.iter_content(chunk_size=1024):
                data+=chunk
                a = data.find(b'\xff\xd8')
                b = data.find(b'\xff\xd9')                
                if a!=-1 and b!=-1:
                    jpg = data[a:b+2]
                    img = Image.open(BytesIO(jpg)).resize([640,480])
                    c = cache.set('snap-%s-%s' % (self.server.id,self.id),img,timeout=5)
                    return img                
        
        except Exception as e:
            import inspect
            print("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))

            img = Image.open(os.path.join(os.path.split(__file__)[0],'static','disconnected.jpg')).resize([640,480])
            return img
        
    def streamurl(self):
        # REQUIRES NGINX CONFIGURATION
        return "%s%02d" % (self.server.stream_url,self.thread_number)

    @property
    def last_events(self):
        return self.event_set.all().order_by('-datetime')[0:20]
        
class ConfigValue(models.Model):
    cam = models.ForeignKey(Cam)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    
    
    class Meta:
        app_label = 'motioncontrol'
    
    def __unicode__(self):
        return self.name    
    
    
class AlertSubscription(models.Model):
    channel = models.CharField(max_length=80,choices=[['email','E-Mail'],['telegram','Telegram Bot']])
    destination = models.CharField(max_length=250)
    cam = models.ForeignKey(Cam)
    alert_motion = models.BooleanField(default=False)
    alert_nomotion = models.BooleanField(default=False)
    alert_nomotion_length = models.TimeField(null=True,blank=True)
    alert_from = models.DateTimeField(null=True,blank=True)
    alert_to = models.DateTimeField(null=True,blank=True)
    enabled = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    pause = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u"%s %s" % (self.channel,self.destination)
    
    class Meta:
        unique_together = (("channel", "destination","cam","alert_motion","alert_nomotion"),)
    
    
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
                self.cam.server.remote_data_folder,
                os.path.split(self.cam.getVal('target_dir').strip())[1]
                ,self.filename
                )
            if os.path.exists(filename):
                img = Image.open(filename) #.resize([320,200]) 
                return img
            else:
                return None
        except Exception as e:
            import inspect
            print("%s:%s" % (inspect.currentframe().f_back.f_code.co_name,e))
            return None
        
@receiver(post_save, sender=Server)
def post_save_server(sender, **kwargs):
    srv = kwargs.get('instance')
    logging.info("POST_SAVE : ConfigValue : %s" % srv)
    # correct url if needed
    if not srv.admin_url.startswith('http'):
        srv.admin_url = "http://%s" % srv.admin_url
        srv.save()
    if not srv.admin_url.endswith('/'):
        srv.admin_url = "%s/" % srv.admin_url
        srv.save()
        
    
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