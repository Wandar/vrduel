# -*- coding: utf-8 -*-
import math
import os
import KBEngine

import KBEDebug
import json
from Constants import *
from typing import Optional

from ServerConstants import *

if 0:from scripts.base.c.space.SpaceBA import SpaceBA
if 0:from scripts.base.GameManager import GameManager
if 0:from scripts.base.c.gamemanager.AccountManagerBA import AccountManagerBA
if 0:from scripts.base.c.gamemanager.SpaceManagerBA import SpaceManagerBA




def _____________________________________basespacefunc():pass

"""
baseappdata[space_871263871263]={"mail":self,"sceneName":self.sceneName,"spaceName":self.spaceName}
baseAppData["p_" + str(self.roomKey)] = 0

"""

def getPublicSpaceNum():
    cnt=0
    for name in KBEngine.baseAppData:
        if name[:6]=="space_":
            cnt+=1
    return cnt



def _____________________________________basespacefuncend():pass



#使用远程tornado进行关机,把所有玩家的数据存入数据库,然后不再处理重要逻辑
def checkShutdown():
    if 'onServerClose' in KBEngine.globalData and KBEngine.globalData["onServerClose"]==True:
        return True
    return False


def checkIsClass(id,className):
    if id not in KBEngine.entities:
        return False
    en=KBEngine.entities[id]
    if en.className!=className:
        return False
    return True


def checkSceneJ():
    a={}
    for key in SCENE_J:
        name=key
        if '/' in key:
            arr=key.split('/')
            name=arr[1]
        if name in a:
            ERROR_MSG("scene chongfu ",name)
        a[name]=1


def getCID():  # type: () -> int
    return int(os.getenv("KBE_COMPONENTID"))

#各种base 游戏管理器1 账号管理器 .....
def isManagerBase():
    return getCID()==1

def getGameManager()-> Optional["GameManager"]:
    return KBEngine.globalData["GameManager"]


def getAccountManagerBA()-> "AccountManagerBA":
    return getGameManager()

def getEntity(id):
    if id in KBEngine.entities:
        return KBEngine.entities[id]
    else:
        return None

def getSpaceManagerBA()->"SpaceManagerBA":
    return KBEngine.globalData["SpaceManager"]



def isBase():
    if KBEngine.component=='baseapp':
        return True
    else:
        return False

def isCell():
    if KBEngine.component=='cellapp':
        return True
    else:
        return False

def posToTilePos(pos):
    return math.floor(pos[0]/MAP_BOX_WIDTH),math.floor(pos[1]/MAP_BOX_WIDTH)




#  0   1    2       3    4        5
#(id,tag,collideGroup,len,collidePos,normal)
def getClostResultInRayResults(results):
    lResult=99999
    trueResult=None
    for result in results:
        l=result[3]
        if l<lResult:
            lResult=l
            trueResult=result
    return trueResult

def normaliseName(s):
    if len(s) > 20:
        s = s[:20]
    s=s.strip()
    while '  ' in s:
        s=s.replace('  ',' ')
    return s