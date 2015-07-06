from django.contrib import admin
from motioncontrol.models import Event, Cam, Server, AlertSubscription
# Register your models here.

class ConfigValueAdmin(admin.ModelAdmin):
    """ Admin Configuration for ConfigValue """
    list_display = ('cam', 'name', 'value')
    list_filter = ('cam__name',)

class CamAdmin(admin.ModelAdmin):
    list_display = (
        'slug', 'server', 'name', 'thread_number', 'output_pictures', 'online', 'last_event','threshold'
    )
    list_filter = ('server__name',)

class EventAdmin(admin.ModelAdmin):
    list_display = ('id','cam','datetime','filename')
    #list_filter = ('server__name',)

class AlertSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id','channel','destination','cam','alert_motion','alert_nomotion','enabled','sent')
    list_filter = ('channel','destination')

admin.site.register(Event,EventAdmin)
admin.site.register(Cam,CamAdmin)
admin.site.register(Server)
admin.site.register(AlertSubscription,AlertSubscriptionAdmin)
#admin.site.register(ConfigValue,ConfigValueAdmin)
