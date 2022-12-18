from django.urls import path
from . import views

urlpatterns = [
    path('accounts/', views.accounts),
    path('createAccount/', views.createAccount),
    path('updateMyPage/', views.updateMyPage),
    path('updateMyNickname/', views.updateMyNickname),
    path('getMyPage/', views.getMyPage),
    path('getHouse/<walletAdress>/', views.getHouse),
    path('sendMsg/', views.sendMsg),
    path('accountCount/', views.accountCount),
    path('saveNft/', views.saveNft),
    path('myMsg/<walletAdress>/', views.myMsg),
    path('myMsg/<walletAdress>/<msgId>/', views.readMyMsg),
    path('follow/<myAdress>/<userAdress>/', views.follow),
    path('like/<myAdress>/<userAdress>/', views.like),
    path('todayRank/', views.todayRank),
    path('makeWallet/', views.makeWallet),
]
