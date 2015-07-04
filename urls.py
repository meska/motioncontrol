from django.conf.urls import url

urlpatterns = [
    url(r'^snapshot/([\w-]+)', 'motioncontrol.views.snapshot'),
    url(r'^cam/([\w-]+)', 'motioncontrol.views.showcam'),
    url(r'^events/([\w-]+)', 'motioncontrol.views.events'),
    url(r'^webhook/', 'motioncontrol.views.webhook'),
    url(r'^api/', 'motioncontrol.views.api'),
    url(r'^cronhook/', 'motioncontrol.views.cronhook'),
    url(r'^ifttthook/(\d+)/(\w+)/(\w+)/', 'motioncontrol.views.ifttthook'),
    url(r'^event_pic/(\d+)', 'motioncontrol.views.event_pic'),
    url(r'^$', 'motioncontrol.views.home'),
  
]
