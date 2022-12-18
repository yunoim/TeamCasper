from rest_framework import serializers
from .models import Account, NftItem, Message


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('walletAdress', 'nickname' ,'myContract', 'myPoint', 'profileImg', 'followed_users', 'followings', 'liked_users', 'likings', 'regDt')
        read_only_fields = ('followed_users', 'followings', 'liked_users', 'likings',)


class NftItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NftItem
        fields = ('id', 'mintId', 'walletAdress', 'locateInfo', 'itemType', 'cnt')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'msgContent', 'onChainYn' ,'sendAccount', 'receiveAccount', 'mailColor', 'mintId', 'regDt')
