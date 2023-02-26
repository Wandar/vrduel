# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2017 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2017/10/16 22:08
from __future__ import annotations
from KBEngine import *
from typing import Dict

from Avatar import Avatar
from c.Component import Component
from util import *
from annos import *

from c.MyCoroutine import MyCoroutine
from c.CheckTime import CheckTime

if 0:from cellapp import KBEngine



class SpaceComponentCE(KBEngine.Entity, Component, CheckTime, MyCoroutine, Reload):
    isSpace=False
    avatars:Dict[int, AvatarCE]=None
    noPoolEns=None #id:weakRef 所有单位,非池子的,池子里的单位由
    _events=None #MESSAGENAME:{id:Functor}

    baseJson=None
    size=(30000,30000)
    # noinspection PyMissingConstructor
    # genMapCE:GenMapCE=None
    objMgrCE:ObjMgrCE=None

    spaceCE:SpaceCE=None

    SHOULD_LOADBASE=True

    isDestroying=False

    def __init__(self):
        pass

    def _initSpaceComponent(self):
        self.spaceCE=self

        self.avatars={}
        self.noPoolEns={}
        self._events={}

        self.genMapCE=self
        self.objMgrCE=self

        KBEngine.Entity.__init__(self)
        Component.__init__(self)
        CheckTime.__init__(self)
        MyCoroutine.__init__(self)
        Reload.__init__(self,False,True)

        # if not self.sceneNameID:
        #     ERROR_MSG("space cell no sceneNameID")

        # scenename=SCENE_J[self.sceneNameID]['name']
        # scenename='WorldScene'
        # self.baseJson= openJson('res/spaces/'+scenename+'/base.json')
        # self._loadMesh(scenename)
        # self.size=(self.baseJson["size"]["width"],self.baseJson["size"]["height"])
        # setMapSize(self.spaceID,self.baseJson["size"]["width"],self.baseJson["size"]["height"])

        self.onLoad()
        self.setInterval(0,0,self.onTimerStart)


    startLoadGeoTime=0
    def _loadMesh(self,scenename):
        self.startLoadGeoTime=time.time()
        addSpaceGeometryMapping(self.spaceID, None, "res/spaces/"+scenename, True, {0: "srv_CAIBakedNavmesh.navmesh"})

    def onSpaceGeometryLoaded(self):
        DEBUG_MSG("loadSpaceGeotry ",time.time()-self.startLoadGeoTime)
        pass


    def onTimerStart(self,tid):
        pass

    def onSpaceInited(self):
        pass

    def onServerClose(self):
        pass


    def createEn(self,entityType,x,y,z):
        return createEntity(entityType,self.spaceID,Vector3(x,y,z),cvec3Zero,{})




    #修正版的raycast,不需要了,C++里修正了
    # def raycast(self,layer:int,src,dst):
    #     l=raycast(self.spaceID,layer,src,dst)
    #     if not l or not pIsZero(l[-1]):#没撞到东西或者撞到东西了
    #         return l
    #     #现在是因为src在墙壁里面
    #     num=0
    #     while 1:
    #         src=pMoveToP(src,dst,20)
    #         if pEqual(src,dst):#太短了
    #             return None
    #         l=raycast(self.spaceID,layer,src,dst)
    #         if not l or not pIsZero(l[-1]):
    #             return l
    #         #重新轮回
    #         num+=1
    #         if num>20:
    #             WARNING_MSG("raycast moved forward over 20")




    # #只有avatar
    # def eachAvatarFunc(self, camp, funcName, *data):
    #     for i,avatar in self.avatars.items():
    #         if avatar.isDestroyed:
    #             continue
    #         else:
    #             if camp == ALL_CAMP or self.avatars[i].camp == camp:
    #                 getattr(avatar, funcName)(*data)

    #包含可能有watcher
    def eachPlayerFunc(self,camp,funcName,*data):
        for i,avatar in self.avatars.items():
            if avatar.isBot:
                continue
            if avatar.isDestroyed:
                continue
            else:
                if camp == ALL_CAMP or avatar.camp == camp:
                    if avatar.watcher and not avatar.watcher.isDestroyed:
                        getattr(avatar.watcher, funcName)(*data)
                    else:
                        getattr(avatar, funcName)(*data)

    # def eachAvatarSetAttr(self,camp,attrName,data):
    #     for i,avatar in self.avatars.items():
    #         if avatar.isDestroyed:
    #             continue
    #         else:
    #             if camp == ALL_CAMP or avatar.camp == camp:
    #                 setattr(self.avatars[i],attrName,data)


    def eachPlayerSetAttr(self,camp,attrName,data):
        for i,avatar in self.avatars.items():
            if avatar.isBot:
                continue
            if avatar.isDestroyed:
                continue
            else:
                if camp == ALL_CAMP or avatar.camp == camp:
                    if avatar.watcher:
                        setattr(avatar.watcher,attrName,data)
                    else:
                        setattr(avatar,attrName,data)


    def spaceOnDestroy(self):
        self.destroySpace()
        self.avatars.clear()
        self.noPoolEns.clear()
        self._events.clear()
        self.offAll()
        # self.genMapCE=None
        self.objMgrCE=None
        self.spaceCE=None


    #注意,只能Entity才能使用这个函数
    def registerMessage(self, msgName, classinst, func):
        if msgName not in self._events:
            self._events[msgName]={}
        self._events[msgName][classinst.id]=Functor(func)

    def deregisterMessage(self, classinst, msgName):
        if msgName not in self._events:
            ERROR_MSG("degester event not esist", classinst, msgName)
            return
        if classinst.id not in self._events[msgName]:
            ERROR_MSG("deregisterMessage not exist id",classinst.id)
            return
        del self._events[msgName][classinst.id]


    def deregisterMessageClass(self,classinst):
        for eventName in self._events:
            if classinst.id in self._events[eventName]:
                del self._events[eventName][classinst.id]




    def fire(self,en,msgName,*arg):
        if msgName not in self._events:
            return
        for id in self._events[msgName]:
            self._events[msgName][id](en,*arg)


    """
    石头发射销毁事件,石头池得到
    玩家发射子弹,发射子弹事件,成就系统可以收到,但是只有在view里面的单位才能收到,那个单位要收大量事件,还需要有事件池,在一段时间内处理事件池的事件
    """
