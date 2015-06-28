from motioncontrol.signals import motion_event
from django.dispatch import receiver
from datetime import datetime

@receiver(motion_event)
def receive_motion_event(sender, **kwargs):
    from motioncontrol.tasks import parseevent
    parseevent(kwargs['data'])
