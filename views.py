from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.conf import settings
from django.core.cache import cache
from threading import Thread
import json
from django.views.decorators.csrf import csrf_exempt

from motioncontrol.models import Server,Cam,Event

PORT_PREFIX = '48'


def home(request):
    return render(request,'home.html',context={'servers':Server.objects.all()})

def showcam(request,cam_slug):
    try:
        cam = Cam.objects.get(slug=cam_slug)
        return render(request,'cam.html',context={'cam':cam})
    except Exception as e:
        return HttpResponseRedirect(redirect_to="/")
    
    
    
def events(request,cam_slug):
    # return image events
    cam = Cam.objects.get(slug=cam_slug)
    return HttpResponse(content=json.dumps(cam.last_events),content_type="text/json")

def event_pic(request,event_id):
    e = Event.objects.get(id=event_id)
    img = e.img()
    if img:
        response = HttpResponse(content_type='image/jpeg')
        img.save(response, "JPEG")
        return response
    else:
        return HttpResponse(content=b'')

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
    