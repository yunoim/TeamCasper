from django.db import models
from django.core.validators import MinValueValidator


class Account(models.Model):
    walletAdress = models.CharField(max_length=300, primary_key=True)
    nickname = models.CharField(max_length=20)
    myContract = models.CharField(max_length=300, blank=True)
    myPoint = models.IntegerField(default=5, validators=[MinValueValidator(0)])
    profileImg = models.CharField(max_length=200, blank=True)
    followed_users = models.ManyToManyField('self', symmetrical=False, related_name='followings', blank=True)
    liked_users = models.ManyToManyField('self', symmetrical=False, related_name='likings', blank=True)
    regDt = models.DateField(auto_now_add=True)


class NftItem(models.Model):
    mintId = models.IntegerField(validators=[MinValueValidator(1)])
    walletAdress = models.CharField(max_length=300)
    locateInfo = models.CharField(max_length=50, blank=True)
    itemType = models.IntegerField()
    cnt = models.IntegerField(validators=[MinValueValidator(0)])

    class Meta:
        unique_together = (('mintId', 'walletAdress'),)
        

class Message(models.Model):
    msgContent = models.TextField(max_length=4000)
    onChainYn = models.CharField(max_length=10)
    sendAccount = models.CharField(max_length=300)
    receiveAccount = models.CharField(max_length=300)
    mintId = models.IntegerField(default=0, blank=True)
    mailColor = models.IntegerField(default=0)
    regDt = models.DateField(auto_now_add=True)
