# custom signals
import django.dispatch

motion_event = django.dispatch.Signal(providing_args=["data"])
motion_alert = django.dispatch.Signal(providing_args=["data"])
picture_alert = django.dispatch.Signal(providing_args=["data"])