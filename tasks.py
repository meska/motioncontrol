import redis
from motioncontrol.models import Event,Cam,Server
from threading import Timer,Thread
from django.conf import settings
import json,os
from datetime import datetime,timedelta
import logging
from django.core.cache import cache
from motioncontrol.signals import motion_alert,picture_alert

def parseevent(data):
    
    try:
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
            #for ua in cam.TelegramUserAlert_set.filter(receive_alerts=True):
            #    ua.sendAlert(event,data[1])
            
    except Exception as e:
        print("mc ParseEvent Error: %s" % e)
    

def purge_old_pics():
    # cleanup old pictures
    for e in Event.objects.filter(datetime__lt=datetime.now()-timedelta(days=30))[0:100]:
        filename = os.path.join( e.cam.server.local_data_folder,os.path.split(e.cam.getVal('target_dir').strip())[1],e.filename)        
        os.unlink(filename)
        e.delete()
        logging.info('%s deleted' % filename)
    # cleanup orphans
    for e in Event.objects.all():
        filename = os.path.join( e.cam.server.local_data_folder,os.path.split(e.cam.getVal('target_dir').strip())[1],e.filename)  
        if not os.path.exists(filename):
            e.delete()
            logging.info('%s deleted' % e)
            
    
def sync_cams():
    # sync cams
    try:
        for s in Server.objects.all():
            for c in s.cams:
                logging.info('Syncin %s' % c)
                c.checksettings()
    except Exception as e:
        logging.error("%s-sync-cams Error: %s"% (__package__,e))
        
        