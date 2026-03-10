from django.db import models
from django.contrib.auth.models import User

class Top_Commenter(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    numComments = models.IntegerField(db_default=0) 
    mostComments = models.BooleanField(db_default=False)