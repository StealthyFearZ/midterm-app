from django.contrib import admin
from .models import Top_Buyer
# Register your models here.

class TopBuyerAdmin(admin.ModelAdmin):
    ordering = ['-numPurchased'] # -numPurchased orders Users in descending order by the number of movies purchased with the top buyer at the top
    list_display = ['user', 'numPurchased', 'mostPurchased']
admin.site.register(Top_Buyer, TopBuyerAdmin)