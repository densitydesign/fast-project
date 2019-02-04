from django.contrib import admin

from .models import *

class CommunityAdmin(admin.ModelAdmin):
    list_display = ['id_backend', 'name']
    list_display_links = ['id_backend', 'name']
admin.site.register(Community, CommunityAdmin)
