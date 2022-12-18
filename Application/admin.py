from django.contrib import admin

from .models import Account, NftItem, Message

admin.site.register(Account)
admin.site.register(NftItem)
admin.site.register(Message)
