# -*- coding: utf-8 -*-
import KBEngine
import time

from ServerDeploy import s_ServerDeploy
import allcards
from dataLoader import reloadData
from fastFunc import isManagerBase
import reloadSystem
import os
from KBEDebug import *
from annos import *


#可以把数据发给所有服务器,还需要经过测试
#动态register和deregister的event暂时废弃
#请使用静态

# g_events={}
# def registerGlobalEvent(msgName,classinst,func):
#     if msgName not in g_events:
#         g_events[msgName]=[]
#     g_events[msgName].append(EventInfo(classinst, func))
#
# def registerGlobalEventNOClass(msgName,func):
#     if msgName not in g_events:
#         g_events[msgName]=[]
#     g_events[msgName].append(EventInfo(None, func))


def onGlobalEventData(key, value):
    _checkBasicEvents(key, value)
    # if key not in g_events:
    #     return
    # for info in g_events[key]: #type:EventInfo
    #     if info.classinst and info.classinst.isDestroyed:
    #         ERROR_MSG("onGlobalEventData class already destroyed",key,info.classinst)
    #         continue
    #     info.callbackfn(*value)  #value一定是tuple


def _checkBasicEvents(key, value):
    if key in KEY_TO_EVENT:
        KEY_TO_EVENT[key]()


def createGameM():
    if isManagerBase():
        KBEngine.createEntityFromDBID("GameManager", 1)


def reloadServerDeploy():
    s_ServerDeploy().reload()


def cleanReloadObject():
    reloadSystem.cleanReloadObject()

def notifyGlobalServer():
    s=KBEngine.globalData["notifyGlobalServer"]
    # if KBEngine.component=='cellapp':
    for id,en in KBEngine.entities.items():
        if 0:en=en #type:AvatarCE
        notifyFunc=getattr(en,"c_showLabel",None)
        if notifyFunc:
            notifyFunc(s)

def notifyGlobalServerWord():
    s=KBEngine.globalData["notifyGlobalServer"]
    # if KBEngine.component=='cellapp':
    for id,en in KBEngine.entities.items():
        if 0:en=en #type:AvatarCE
        notifyFunc=getattr(en,"c_showLabel",None)
        if notifyFunc:
            notifyFunc(s)

    # elif KBEngine.component=='baseapp':


def closingNotify():
    t=KBEngine.globalData["closingNotify"]
    for id,en in KBEngine.entities.items():
        if 0:en=en #type:AvatarCE
        notifyFunc=getattr(en,"c_showLabel",None)
        if notifyFunc:
            notifyFunc("server will reboot in %d minutes"%t)


def reloadSp():
    CID = int(os.getenv("KBE_COMPONENTID"))
    DEBUG_MSG("%s %d reload" % (KBEngine.component, CID))

    a = time.time()
    reloadSystem.reloadAllModule()
    reloadSystem.merge_g_allComponents()
    reloadSystem.checkEntitiesAttrConflict()
    KBEngine.reloadScript(True)
    reloadData()
    allcards.mergeAllCards(True)
    DEBUG_MSG("reload use time " + str(time.time() - a))



def cleanGarbage():
    gar = KBEngine.entities.garbages
    keyList=list(gar.keys())
    if len(keyList):
        for key in keyList:
            if key in gar: #maybe destroyed together
                en=gar[key]
                en.__dict__.clear()
                INFO_MSG("clean garbage %d %s"%(key,en.className))
        INFO_MSG("clean end garbage=%d"%len(gar.keys()))

def onServerClose():
    if KBEngine.component=='baseapp':
        KBEngine.forbidLogin()
    isCell=KBEngine.component=="cellapp"
    enL=[]
    for i,entity in KBEngine.entities.items():
        if isCell and entity.position.x<0:
            pass
        else:
            f=getattr(entity,'onServerClose',None)
            if f:
                enL.append(entity)
    for en in enL:
        f=getattr(en,'onServerClose',None)
        f()




def _fireGlobalEvent(msgName, arg):
    KBEngine.globalData[msgName] = arg
    onGlobalEventData(msgName, arg)


# def deregisterGlobalEvent(classinst, msgName):
#     if msgName not in g_events:
#         ERROR_MSG("deregester  global event not esist", classinst, msgName)
#         return
#     arr=g_events[msgName]
#     for i in range(len(arr)) :
#         if arr[i].classinst==classinst:
#             del arr[i]
#
# def deregisterGlobalEventByClass(classinst):
#     for eventName in g_events:
#         evtlst=g_events[eventName]
#         for i in range(len(evtlst)):
#             if evtlst[i].classinst==classinst:
#                 del evtlst[i]
#
# def deregisterGlobalEventByMsgName(msgName):
#     del g_events[msgName]


KEY_TO_EVENT = {
    "reloadScript": reloadSp,
    "reloadData": reloadData,
    "createGameManager": createGameM,
    "reloadServerDeploy": reloadServerDeploy,
    "cleanReloadObject": cleanReloadObject,
    "cleanGar": cleanGarbage,
    "notifyGlobalServer":notifyGlobalServer,
    "notifyGlobalServerWord":notifyGlobalServerWord,
    "closingNotify":closingNotify,
    "onServerClose":onServerClose
}



def fire_reloadScript():
    _fireGlobalEvent("reloadScript", True)



def fire_reloadData():
    _fireGlobalEvent("reloadData", True)


def fire_reloadServerDeploy():
    _fireGlobalEvent("reloadServerDeploy", True)


def fire_createGameManager():
    _fireGlobalEvent("createGameManager", True)


def fire_cleanReloadObject():
    _fireGlobalEvent("cleanReloadObject", True)


def fire_cleanGarbages():
    _fireGlobalEvent("cleanGar", True)


def fire_onServerClose():
    _fireGlobalEvent("onServerClose",True)

def fire_closingNotify(t):
    _fireGlobalEvent("closingNotify",t)

def fire_():
    _fireGlobalEvent("onServerClose",True)

def fire_notifyGlobalServer(s):
    _fireGlobalEvent("notifyGlobalServer",s)

def fire_notifyGlobalServerWord(s):
    _fireGlobalEvent("notifyGlobalServerWord",s)


# def fire_globalChat(msg):
#     _fireGlobalEvent("c", msg)
