from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from base64 import b64decode,b64encode
from PIL import Image
import cStringIO
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
    except Exception,e:
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
    except Exception,e:
        return HttpResponse(b"",content_type='image/jpeg')
    
    img = cam.snapshot()
    response = HttpResponse(content_type='image/jpeg')
    img.save(response, "JPEG")
    return response     
    


@csrf_exempt
def webhook(request):
    from motioncontrol.tasks import parseevent
    try:
        parseevent(request.body)
    except Exception,e:
        print "Error WebHook motion %s" % e 
    
    return HttpResponse()