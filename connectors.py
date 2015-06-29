from motioncontrol.signals import motion_event,picture_alert
from django.dispatch import receiver

@receiver(motion_event)
def receive_motion_event(sender, **kwargs):
    from motioncontrol.tasks import parseevent
    parseevent(kwargs['data'])


#@receiver(picture_alert)
#def receive_picture_alert(sender, **kwargs):
#    event=kwargs['data']
#    print("Picture Alert")
    
