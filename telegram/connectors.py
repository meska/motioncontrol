# telegram connectors for motioncontrol
from motioncontrol.signals import picture_alert
from telegrambot.signals import message_received
from django.dispatch import receiver
from django.conf import settings
from io import BytesIO

@receiver(picture_alert)
def receive_picture_alert(sender, **kwargs):
    event=kwargs['data']
    from motioncontrol.models import AlertSubscription
    als = AlertSubscription.objects.filter(cam=event.cam,enabled=True,alert_motion=True,pause=False)
    for a in als:
        if a.channel == 'telegram':
            from telegrambot.wrapper import Bot
            img = event.img()
            if img:
                b = Bot(settings.TELEGRAM_BOT_TOKEN)
                fp = BytesIO()
                img.save(fp,'JPEG')
                fp.seek(0)            
                b.sendPhoto(a.destination, fp, caption='motion alert %s' % event.cam.name)
                #cache.set("%s-%s-%s" % (__name__,tipo,self.user.user_id),True,30)    

    print("Picture Alert")
    
@receiver(message_received)
def receive_message(sender, **kwargs):
    from motioncontrol.telegram.parser import Parser
    p = Parser(sender)
    p.parse(kwargs['message'])    