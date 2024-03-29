from django.db import models

# Create your models here.


class Message(models.Model):
    sender = models.CharField(max_length=100) 
    content = models.TextField()
    timestamp = models.IntegerField()
    room_name = models.CharField(max_length=100)

class Chat(models.Model):
    idUser_sender = models.CharField(max_length=128, unique=False, null=True, default=None)
    idUser_reciever = models.CharField(max_length=128, unique=False, null=True, default=None)    
    room_name = models.CharField(max_length=100)
    last_conection =  models.IntegerField()
    email = models.CharField(max_length=100)
    creator = models.BooleanField()
    id_chat = models.CharField(max_length=128, unique=True, null=True, default=None)
