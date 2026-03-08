from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Top_Buyer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    numPurchased = models.IntegerField(db_default=0) #Number purchased starts at 0 so make sure to sanity check total movies purchased vs. movies purchased after model migration
    mostPurchased = models.BooleanField(db_default=False)
