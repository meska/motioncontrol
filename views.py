from django.shortcuts import render,HttpResponse,HttpResponseRedirect,get_object_or_404
from django.conf import settings
from django.core.cache import cache
from threading import Thread
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from motioncontrol.models import Server,Cam,Event

PORT_PREFIX = '48'

@login_required
def home(request):
    return render(request,'home.jade',context={'servers':Server.objects.all()})

@login_required
def showcam(request,cam_slug):
    cam = get_object_or_404(Cam,slug=cam_slug)
    return render(request,'cam.jade',context={'cam':cam})

    
    
@login_required    
def events(request,cam_slug):
    # return image events
    cam = Cam.objects.get(slug=cam_slug)
    return HttpResponse(content=json.dumps(cam.last_events),content_type="text/json")

@login_required
def event_pic(request,event_id):
    e = Event.objects.get(id=event_id)
    img = e.img()
    if img:
        response = HttpResponse(content_type='image/jpeg')
        img.save(response, "JPEG")
        return response
    else:
        return HttpResponse(content=b'')

@login_required
def snapshot(request,cam_slug):
    try:
        cam = Cam.objects.get(slug=cam_slug)
    except Exception as e:
        return HttpResponse(b"",content_type='image/jpeg')
    
    img = cam.snapshot()
    if img:
        response = HttpResponse(content_type='image/jpeg')
        img.save(response, "JPEG")
        return response     
    else:
        return HttpResponse()
    


@csrf_exempt
def webhook(request):
    from motioncontrol.signals import motion_event
    motion_event.send(__name__,data=json.loads(request.body.decode('utf8')))
    
    return HttpResponse()

@csrf_exempt
def ifttthook(request,user_id,cmd,param):
    if not settings.MOTION_TELEGRAM_PLUGIN:
        return HttpResponse('telegram plugin disabled')
    
    from telegrambot.models import TelegramUser
    from telegrambot.wrapper import Bot
    from motioncontrol.telegram.parser import Parser
    from motioncontrol.models import AlertSubscription

    try:
        user = TelegramUser.objects.get(user_id=user_id)
        bot = Bot(settings.TELEGRAM_BOT_TOKEN)

        if cmd == 'pause' and param == 'all':
            for a in AlertSubscription.objects.filter(destination=user.user_id,enabled=True):
                a.pause = True
                a.save()
            bot.sendMessage(user.user_id,"Alerts disattivati via ifttt")
            
        if cmd == 'unpause' and param == 'all':
            for a in AlertSubscription.objects.filter(destination=user.user_id,enabled=True):
                a.pause = False
                a.save()
            bot.sendMessage(user.user_id,"Alerts attivati via ifttt")

        if param.isdigit():
            c = Cam.objects.get(id=int(param))
            alert,created = AlertSubscription.objects.get_or_create(
                channel = 'telegram',
                destination = user.user_id,
                cam = c,
                alert_motion = True if cmd.endswith('motion') else False,
                alert_nomotion = True if cmd.endswith('pause') else False,
                enabled = True if cmd.startswith('on') else False,
                pause = False
            )            
        
            bot.sendMessage(user.user_id,"%s alert on %s %s via ifttt" % ( 
                'Motion' if cmd.endswith('motion') else 'Pause',
                c.name,
                'enabled' if cmd.startswith('on') else 'disabled'
            ))
        
    except:
        # not writing any errors for tinkerers
        pass
    return HttpResponse()

@csrf_exempt
def cronhook(request):
    """
      simple cront management, 
      put this on your crontab:
      */5 * * * * curl -s http://yoursite.com/mc/cronhook/ > /dev/null 2>&1
    """

    # manual requests
    do = request.GET.get('do')
    if do == 'sync_cams':
        from motioncontrol.tasks import sync_cams
        sync_cams()
    elif do == 'purge_old_pics':
        from motioncontrol.tasks import purge_old_pics
        purge_old_pics()
    elif do =='check_onpause':
        if settings.MOTION_TELEGRAM_PLUGIN:
            from motioncontrol.tasks import check_onpause
            check_onpause()        
    
    # sync cam settings every 10 minutes
    if not cache.get("%s-sync-cams" % __package__):
        from motioncontrol.tasks import sync_cams
        Thread(target=sync_cams).start()
        cache.set("%s-sync-cams" % __package__,True,600)

    # purge old pics every hour
    if not cache.get("%s-purge" % __package__):
        from motioncontrol.tasks import purge_old_pics
        Thread(target=purge_old_pics).start()
        cache.set("%s-purge" % __package__,True,3600)    

    # check for pause alerts
    if settings.MOTION_TELEGRAM_PLUGIN:
        if not cache.get("%s-onpause" % __package__):
            from motioncontrol.tasks import check_onpause
            Thread(target=check_onpause).start()
            cache.set("%s-onpause" % __package__,True,600)      
    
    return HttpResponse('ok')
    