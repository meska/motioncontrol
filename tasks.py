import redis
from motioncontrol.models import Event,Cam,Server
from threading import Timer,Thread
from django.conf import settings
import json,os
from datetime import datetime,timedelta
import logging
from django.core.cache import cache

def parseevent(s):

    # eventualmente avvio altri tasks
    if not cache.get("%s-sync-cams" % __package__):
        Thread(target=sync_cams).start()
        cache.set("%s-sync-cams" % __package__,True,600)

    if not cache.get("%s-purge" % __package__):
        Thread(target=purge_old_pics).start()
        cache.set("%s-purge" % __package__,True,3600)    
    
    try:
        data = json.loads(s)
        if data[1] == "lost":
            cam = Cam.objects.get(slug=data[2])
            cam.online = False
            cam.save()

        if data[1] == "motion":
            cam = Cam.objects.get(slug=data[2])
            cam.online = True
            cam.save()            
            #for ua in cam.TelegramUserAlert_set.filter(receive_alerts=True):
            #    ua.sendAlert(cam,data[1])            

        if data[1] == "picture":
            cam = Cam.objects.get(slug=data[2])
            cam.online = True
            cam.save()      
            event,created = Event.objects.get_or_create(cam=cam,datetime=datetime.strptime(data[3]+data[4],"%Y%m%d%H%M%S"),event_type=data[5],filename=os.path.split(data[7])[1])    

            for ua in cam.TelegramUserAlert_set.filter(receive_alerts=True):
                ua.sendAlert(event,data[1])
            
    except Exception,e:
        print "mc ParseEvent Error: %s" % e
    

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
    except Exception,e:
        logging.error("%s-sync-cams Error: %s"% (__package__,e))
        
        