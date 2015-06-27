from django.contrib import admin
from motioncontrol.models import *
# Register your models here.

class ConfigValueAdmin(admin.ModelAdmin):
    list_display = ('cam', 'name', 'value')
    list_filter = ('cam__name',)

class CamAdmin(admin.ModelAdmin):
    list_display = ('slug','server', 'name', 'thread_number','output_pictures')
    list_filter = ('server__name',)


admin.site.register(Event)
admin.site.register(Cam,CamAdmin)
admin.site.register(Server)

#admin.site.register(ConfigValue,ConfigValueAdmin)