from django.conf.urls import include, url

urlpatterns = [
    url(r'^snapshot/([\w-]+)', 'motioncontrol.views.snapshot'),
    url(r'^cam/([\w-]+)', 'motioncontrol.views.showcam'),
    url(r'^events/([\w-]+)', 'motioncontrol.views.events'),
    url(r'^webhook/', 'motioncontrol.views.webhook'),
    url(r'^event_pic/(\d+)', 'motioncontrol.views.event_pic'),
    url(r'^$', 'motioncontrol.views.home'),
  
]
