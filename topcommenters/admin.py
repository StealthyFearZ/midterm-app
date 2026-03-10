from django.contrib import admin

from django.contrib import admin
from .models import Top_Commenter

class TopCommenterAdmin(admin.ModelAdmin):
    ordering = ['-numComments'] 
    list_display = ['user', 'numComments', 'mostComments']
    
admin.site.register(Top_Commenter, TopCommenterAdmin)