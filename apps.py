from django.apps import AppConfig
from django.conf import settings
from threading import Timer
import sys


def pull_motion_event(queuename):
    # pull motion events from redis and dispatch a signal 
    import redis,json
    out = []
    r = redis.StrictRedis(host=settings.MOTION_REDIS_SERVER, port=6379, db=0)
    s = r.lpop(queuename)
    if s:
        from motioncontrol.signals import motion_event
        motion_event.send(__name__,data=json.loads(s.decode('utf8')))

    Timer(30,pull_motion_event,args=[settings.MOTION_REDIS_CHANNEL,]).start()
    

class MotionControlConfig(AppConfig):
    name = 'motioncontrol'
    verbose_name = "Motion Control"

    def ready(self):
        if 'runserver' in sys.argv:
            if settings.MOTION_REDIS_CHANNEL:
                # enable redis poller for motion events
                from threading import Timer
                Timer(10,pull_motion_event,args=[settings.MOTION_REDIS_CHANNEL,]).start()
            
            
        #if settings.MOTION_TELEGRAM_PLUGIN:
        #    import motioncontrol.telegram.connectors
        #    from motioncontrol.telegram.parser import check_onpause
        #    from threading import Timer
        #    Timer(10,check_onpause).start()
            
        import motioncontrol.signals
        import motioncontrol.connectors