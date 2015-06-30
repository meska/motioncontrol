from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from base64 import b64decode,b64encode
from PIL import Image
from io import BytesIO
import logging
from datetime import datetime
from django.core.cache import cache
from django.template.defaultfilters import slugify
from threading import Thread
import zlib
import json
import os,sys
from django.views.decorators.csrf import csrf_exempt

from motioncontrol.models import Server,Cam,Event

PORT_PREFIX = '48'


def home(request):
    return render(request,'home.html',context={'servers':Server.objects.all()})

def showcam(request,cam_slug):
    try:
        cam = Cam.objects.get(slug=cam_slug)
    except Exception as e:
        return HttpResponseRedirect(redirect_to="/"
                                    )
    return render(request,'cam.html',context={'cam':Cam.objects.get(slug=cam_slug)})
    
    
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
      simple cront management
      put this on your crontab:
      */5 * * * * curl -s http://yoursite.com/mc/cronhook/ > /dev/null 2>&1
    """

    # sync cam settings every 10 minutes
    if not cache.get("%s-sync-cams" % __package__):
        from motioncontrol.tasks import sync_cams
        Thread(target=sync_cams).start()
        cache.set("%s-sync-cams" % __package__,True,600)

    if not cache.get("%s-purge" % __package__):
        from motioncontrol.tasks import purge_old_pics
        Thread(target=purge_old_pics).start()
        cache.set("%s-purge" % __package__,True,3600)    

    if settings.MOTION_TELEGRAM_PLUGIN:
        if not cache.get("%s-onpause" % __package__):
            from motioncontrol.telegram.parser import check_onpause
            Thread(target=check_onpause).start()
            cache.set("%s-onpause" % __package__,True,600)      
    
    