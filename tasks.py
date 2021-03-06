from motioncontrol.models import Event,Cam,Server
from threading import Thread
from django.conf import settings
import os
import redis
from datetime import datetime,timedelta
import logging
from motioncontrol.signals import motion_alert,picture_alert


def check_onpause():
    # check for pause events
    from io import BytesIO
    from motioncontrol.models import AlertSubscription
    for a in AlertSubscription.objects.filter(alert_nomotion=True,enabled=True,sent=False,pause=False):
        
        r = redis.StrictRedis(host=settings.MOTION_REDIS_SERVER, port=6379, db=0)
        res = r.get('motion-event-%s' % a.cam.slug)
    
        if not res:        
            # idle
            from telegrambot.wrapper import Bot
            b = Bot(settings.TELEGRAM_BOT_TOKEN)
            b.sendMessage(a.destination,"Nessun movimento su /s_%s" % (a.cam.name.replace(' ','_')))
            a.sent = True
            a.save()            
            #img = a.cam.snapshot()
            #if img:
                #b = Bot(settings.TELEGRAM_BOT_TOKEN)
                #fp = BytesIO()
                #img.save(fp,'JPEG')
                #fp.seek(0)            
                #b.sendPhoto(a.destination, fp, caption='pause alert %s' % a.cam.name)
                
                #a.sent = True
                #a.save()

    # check for resume            
    for a in AlertSubscription.objects.filter(alert_nomotion=True,enabled=True,sent=True,pause=False):
        r = redis.StrictRedis(host=settings.MOTION_REDIS_SERVER, port=6379, db=0)
        res = r.get('motion-event-%s' % a.cam.slug)
    
        if res:        
            # moving
            from telegrambot.wrapper import Bot
            b = Bot(settings.TELEGRAM_BOT_TOKEN)
            b.sendMessage(a.destination,"Movimento ripristinato su /s_%s" % (a.cam.name.replace(' ','_')))
            a.sent = False
            a.save()               
            #img = a.cam.snapshot()
            #if img:
                #b = Bot(settings.TELEGRAM_BOT_TOKEN)
                #fp = BytesIO()
                #img.save(fp,'JPEG')
                #fp.seek(0)            
                #b.sendPhoto(a.destination, fp, caption='resume alert %s' % a.cam.name)
                
                #a.sent = False
                #a.save()       

def parseevent(data):
    if data[1] == "lost":
        cam = Cam.objects.get(slug=data[2])
        cam.save()

    if data[1] == "motion":
        cam = Cam.objects.get(slug=data[2])
        cam.last_event = datetime.strptime("%s%s" % (data[3],data[4]),"%Y%m%d%H%M%S")
        cam.save()     
        motion_alert.send(cam,data=data)
     

    if data[1] == "picture":
        cam = Cam.objects.get(slug=data[2])
        cam.last_event = datetime.strptime("%s%s" % (data[3],data[4]),"%Y%m%d%H%M%S")
        cam.save()     
        event,created = Event.objects.get_or_create(cam=cam,datetime=datetime.strptime(data[3]+data[4],"%Y%m%d%H%M%S"),event_type=data[5],filename=os.path.split(data[7])[1])    
        if created:
            picture_alert.send(cam,data=event)

    

def purge_old_pics():


    #cleanup orphans files
    #for c in Cam.objects.all():
    #    print(c.getVal('target_dir').strip())


    # cleanup old pictures, date depend from threshold
    
    for e in Event.objects.filter(datetime__lt=datetime.now()-timedelta(days=2),cam__threshold__lte=1000):
        filename = os.path.join( e.cam.server.remote_data_folder,os.path.split(e.cam.getVal('target_dir').strip())[1],e.filename) 
        if os.path.exists(filename):
            try:
                os.unlink(filename)
                e.delete()
                logging.info('%s deleted' % filename)    
            except:
                pass
    
    for e in Event.objects.filter(datetime__lt=datetime.now()-timedelta(days=15),cam__threshold__gt=1000):
        filename = os.path.join( e.cam.server.remote_data_folder,os.path.split(e.cam.getVal('target_dir').strip())[1],e.filename)        
        if os.path.exists(filename):
            os.unlink(filename)
            e.delete()
            logging.info('%s deleted' % filename)

    # cleanup orphans records
    for e in Event.objects.all():
        filename = os.path.join( e.cam.server.remote_data_folder,os.path.split(e.cam.getVal('target_dir').strip())[1],e.filename)  
        if not os.path.exists(filename):
            e.delete()
            logging.info('%s deleted' % e)
    
            
    
def sync_cams():
    # sync cams with config file
    
    for s in Server.objects.all():
        for c in s.cams:
            c.checksettings()        