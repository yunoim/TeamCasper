from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import AccountSerializer, NftItemSerializer, MessageSerializer
from .models import Account, NftItem, Message
from datetime import date
from random import randint
from django.db.models import Q, Count
from pathlib import Path
import json, os, string

from binance_chain.wallet import Wallet
from binance_chain.environment import BinanceEnvironment

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_DIR = os.path.join(BASE_DIR, '.secrets')
ACCOUNT_IMG_DIR = os.path.join(BASE_DIR, 'accountImg')
secrets = json.load(open(os.path.join(SECRET_DIR, 'secret.json'), 'rb'))


def generate_mnemonic():
    words = secrets['WORDS']
    ret = words[randint(0, len(words))]
    for _ in range(11):
        ret += ' ' + words[randint(0, len(words))]
    
    return ret


def contain_special_chr(param):
    for c in param:
        if c in string.punctuation:
            return True
    return False


def validate_no_special_chr(param):
    if contain_special_chr(param):
        return False
    return True


@api_view(['GET'])
def accounts(request):
    accounts = Account.objects.all()
    serializer = AccountSerializer(accounts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def accountCount(request):
    accounts = Account.objects.all()
    cnt = accounts.count()
    return Response(cnt+1)


@api_view(['POST'])
def createAccount(request):
    newWalletAdress = request.data.get("walletAdress")
    accountVo = Account.objects.filter(walletAdress=newWalletAdress)
    if accountVo:
        serializer = AccountSerializer(accountVo)
        return Response(True, status=status.HTTP_200_OK)
    serializer = AccountSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(nickname="newUser" + str(Account.objects.all().count()), myPoint=5)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def myMsg(request, walletAdress):
    if Account.objects.filter(walletAdress=walletAdress).exists():
        receiveMsg = Message.objects.filter(receiveAccount=walletAdress)
        serializer = MessageSerializer(receiveMsg, many=True)
        sendMsg = Message.objects.filter(sendAccount=walletAdress)
        serializer2 = MessageSerializer(sendMsg, many=True)
        accountVo = Account.objects.get(walletAdress=walletAdress)
        serializer3 = AccountSerializer(accountVo)

        ret = [serializer.data, serializer2.data, serializer3.data]

        return Response(ret)
    else:
        return Response(False)


@api_view(['POST'])
def sendMsg(request):
    msgInfo = request.data.get("msgInfo")
    nftInfo = request.data.get("nftInfo")
    serializer = MessageSerializer(data=msgInfo)
    sendAccount = Account.objects.get(walletAdress=msgInfo['sendAccount'])

    if not sendAccount:
        return Response('not exist sendAccount')
    
    receiveAccount = Account.objects.get(walletAdress=msgInfo['receiveAccount'])
    if not receiveAccount:
        return Response('not exist receiveAccount')

    if sendAccount.myPoint > 1:
        sendAccount.myPoint -= 1
        sendAccount.save()

    # 일단 FE 에서 민팅 --> smartContract 민팅 정보 받아오기
    mintId = msgInfo["mintId"]
    walletAdress = nftInfo["walletAdress"]
    locateInfo = ""
    itemType = nftInfo["itemType"]
    cnt = nftInfo["cnt"]
    if NftItem.objects.filter(walletAdress=walletAdress, mintId=mintId).exists():
        nftItemVo = NftItem.objects.get(walletAdress=walletAdress, mintId=mintId)
        nftItemVo.cnt = cnt
        nftItemVo.save()
    else:
        nftItem = NftItem(mintId=mintId, walletAdress=walletAdress, locateInfo=locateInfo, itemType=itemType, cnt=cnt)
        nftItem.save()

    if serializer.is_valid(raise_exception=True):
        serializer.save(mintId=mintId)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def makeWallet(request):
    testnet_env = BinanceEnvironment.get_testnet_env()
    phrase = generate_mnemonic()
    wallet = Wallet.create_wallet_from_mnemonic(phrase, env=testnet_env)
    
    newWallet = dict()
    newWallet['adress'] = wallet.address
    newWallet['private_key'] = wallet.private_key
    newWallet['public_key_hex'] = wallet.public_key_hex
    newWallet['phrase'] = phrase

    return Response(newWallet, status=status.HTTP_201_CREATED)


# 방꾸 페이지
@api_view(['POST'])
def getMyPage(request):
    nftList = request.data.get("nftList")
    walletAdress = ""
    content = ""
    if nftList:
        walletAdress = nftList[0]["walletAdress"]
    
    if not Account.objects.filter(walletAdress=walletAdress).exists():
        content = "Not exists walletAdress"
        return Response(False, status=status.HTTP_404_NOT_FOUND)

    nftInfo = []
    for nft in nftList:
        mintId = nft["mintId"]
        cnt = nft["cnt"]
        itemType=nft["itemType"]
        if NftItem.objects.filter(mintId=mintId, walletAdress=walletAdress).exists():
            nftItemVo = NftItem.objects.get(mintId=mintId, walletAdress=walletAdress)
            nftItemVo.cnt = cnt
            nftItemVo.save()
            serializer = NftItemSerializer(nftItemVo)
            nftInfo.append(serializer.data)
        else:
            nftItem = NftItem(mintId=mintId, walletAdress=walletAdress, locateInfo="", itemType=itemType, cnt=cnt)
            nftItem.save()
            serializer = NftItemSerializer(nftItem)
            nftInfo.append(serializer.data)

    return Response(nftInfo)


# 집 구경
@api_view(['GET'])
def getHouse(request, walletAdress):
    ret = []
    content = ""
    if Account.objects.filter(walletAdress=walletAdress).exists():
        account = Account.objects.get(walletAdress=walletAdress)
        serializer = AccountSerializer(account)
        ret.append(serializer.data)

        q = Q()
        q &= Q(walletAdress=walletAdress)
        q &= ~Q(locateInfo = "")
        q &= ~Q(cnt = 0)
        nftInfo = NftItem.objects.filter(q)
        serializer2 = NftItemSerializer(nftInfo, many=True)
        ret.append(serializer2.data)

        return Response(ret)
    else:
        content = "not exists walletAdress"
        return Response(False, status=status.HTTP_404_NOT_FOUND)


# 방꾸 저장
@api_view(['PUT'])
def updateMyPage(request):
    nftList = request.data.get("nftList")
    walletAdress = ""
    if nftList:
        walletAdress = nftList[0]["walletAdress"]
    
    if not Account.objects.filter(walletAdress=walletAdress).exists():
        content = "Not exists walletAdress"
        return Response(False, status=status.HTTP_404_NOT_FOUND)

    ret = []
    for nft in nftList:
        nftItemVo = NftItem.objects.get(mintId=nft["mintId"], walletAdress=walletAdress)
        nftItemVo.locateInfo = nft["locateInfo"]
        nftItemVo.save()
        serializer = NftItemSerializer(nftItemVo)
        ret.append(serializer.data)
    
    return Response(ret, status=status.HTTP_201_CREATED)


# 닉네임 변경 저장
@api_view(['PUT'])
def updateMyNickname(request):
    walletAdress = request.data.get("walletAdress")
    nickname = request.data.get("nickname")
    content = ""

    if not nickname or len(nickname) > 20 or not validate_no_special_chr(nickname):
        content = "Invalid nickname"
        return Response(False, status=status.HTTP_400_BAD_REQUEST)

    if Account.objects.filter(walletAdress=walletAdress).exists():
        accountVo = Account.objects.get(walletAdress=walletAdress)
        accountVo.nickname = nickname
        accountVo.save()
        serializer = AccountSerializer(accountVo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    else:
        content = "Not exists walletAdress"
        return Response(False, status=status.HTTP_404_NOT_FOUND)


# 메시지 상세 GET
@api_view(['GET'])
def readMyMsg(request, walletAdress, msgId):
    content = ""
    if Message.objects.filter(id=msgId):
        myMsg = Message.objects.get(id=msgId)
        if myMsg.receiveAccount != walletAdress:
            content = "Invalid walletAdress"
            return Response(False, status=status.HTTP_400_BAD_REQUEST)

        serializer = MessageSerializer(myMsg)
        return Response(serializer.data)
    else:
        content = "Not exists msg"
        return Response(False, status=status.HTTP_404_NOT_FOUND)


# NFT 저장 (NFT 확인 하는 모든 페이지에서 실행)
@api_view(['POST'])
def saveNft(request):
    nftInfoList = request.data.get("nftInfoList")
    walletAdress = ""
    content = ""
    if nftInfoList:
        walletAdress = nftInfoList[0]["walletAdress"]
    
    if not Account.objects.filter(walletAdress=walletAdress).exists():
        content = "Not exists walletAdress"
        return Response(False, status=status.HTTP_404_NOT_FOUND)

    tokenIdList = []

    for nftInfo in nftInfoList:
        mintId = nftInfo["mintId"]
        itemType = nftInfo["itemType"]
        tokenIdList.append(mintId)
        if NftItem.objects.filter(mintId=mintId, walletAdress=walletAdress).exists():
            nftItemVo = NftItem.objects.get(mintId=mintId, walletAdress=walletAdress)
            nftItemVo.cnt = nftInfo["cnt"]
            nftItemVo.save()
        else:
            nftItem = NftItem(mintId=mintId, walletAdress=walletAdress, locateInfo="", itemType=itemType, cnt=nftInfo["cnt"])
            nftItem.save()
    
    # 검색된 (tokenIdList에 들어있는) nft 외에, 현재 walletAdress가 가지고 있다는 정보가 DB에 있는 애들은 locateInfo = "", cnt = 0 처리 해야한다.
    q = Q()
    q &= Q(walletAdress=walletAdress)
    for tId in tokenIdList:
        q &= ~Q(mintId = tId)
    
    nftItemVo2 = NftItem.objects.filter(q)
    serializer2 = NftItemSerializer(nftItemVo2, many=True)
    for sData in serializer2.data:
        nftItemVo3 = NftItem.objects.get(walletAdress=walletAdress, mintId=sData["mintId"])
        nftItemVo3.cnt = 0
        nftItemVo3.locateInfo = ""
        nftItemVo3.save()

    return Response(True, status=status.HTTP_201_CREATED)


# Follow / UnFollow
@api_view(['POST'])
def follow(request, myAdress, userAdress):
    person = get_object_or_404(Account, walletAdress=userAdress)
    me = get_object_or_404(Account, walletAdress=myAdress)
    if person != me:
        if me.followings.filter(walletAdress=person.walletAdress).exists():
            me.followings.remove(person)
            following = False
            
        else:
            me.followings.add(person)
            following = True
            
        return Response(following)
    
    return Response(me.walletAdress)


# Like / UnLike
@api_view(['POST'])
def like(request, myAdress, userAdress):
    person = get_object_or_404(Account, walletAdress=userAdress)
    me = get_object_or_404(Account, walletAdress=myAdress)
    if person != me:
        if me.likings.filter(walletAdress=person.walletAdress).exists():
            me.likings.remove(person)
            likings = False
            
        else:
            me.likings.add(person)
            likings = True
            
        return Response(likings)
    
    return Response(me.walletAdress)


# Today's Ranking (1 ~ 10)
@api_view(['GET'])
def todayRank(request):
    accountsCnt = max(10, Account.objects.all().count())
    accounts = Account.objects.annotate(count=Count('liked_users')).order_by('-count')[:accountsCnt]
    serializer = AccountSerializer(accounts, many=True)
    return Response(serializer.data)
