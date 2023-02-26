# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2017 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2017/9/13 3:24
from KBEngine import *

from c.MyCoroutine import MyCoroutine
from common.EventSystem import EventSystem
from mydicts import mySpaces

from util import *

from c.CheckTime import CheckTime
from c.Component import Component
from annos import *

if 0: from cellapp import KBEngine


class ComponentCE(KBEngine.Entity, Component, CheckTime, EventSystem, MyCoroutine, Reload):
    active = True
    POOLOBJ = False  #是否是池子里的单位,不要手动设置
    NO_START = False


    ENTITY_SHOULD_STORE_WITNESS=False #bullet,currently no use
    witnessedPlayers=None

    # _messages={}
    space = None

    moveId=0

    CAN_DAMAGE=False

    isDestroying=False
    def __init__(self):
        pass

    # 真实的__init__,因为不能把__init__暴露给component,所以下面这个才是真正的初始化函数
    def _initCellComponent(self):
        Entity.__init__(self)
        Component.__init__(self)
        CheckTime.__init__(self)
        EventSystem.__init__(self)
        MyCoroutine.__init__(self)
        Reload.__init__(self,False,True)

        if self.ENTITY_SHOULD_STORE_WITNESS:
            self.witnessedPlayers={}

        # self.space = cellAppData["space_%d" % self.spaceID]  #type:Space
        self.space = mySpaces[self.spaceID]  #type:Space
        self.onLoad()

        if not self.POOLOBJ:
            self.space.noPoolEns[self.id] = weakref.ref(self)
        if not self.NO_START:
            self.setInterval(0, 0, self.onTimerStart)

    def onTimerStart(self, tid):
        pass

    # 便利的功能
    # def setAngle(self,angle):
    #     self.setRotation(angle*math.pi/180)


    def getDistance(self, en):
        return pDistance(en.getPos(), self.getPos())

    def turnToPos(self, pos):
        rad = math.atan2(pos.x - self.position.x, pos.z - self.position.z)
        self.setRad(rad)


    # def move(self, v, t=0, acc=0, userData=0, isDirect=False, isFace=False, isWallCollide=False,
    #          wallLayer=0,wallCollideRadius=0):
    #     if pIsZero(v):
    #         self.moveToPointAcc(self.getPos(), 0, acc, 0, isDirect, userData, isFace, False)
    #         return None
    #     if t == 0 and acc >= 0:
    #         ERROR_MSG("acc>=0")
    #         return None
    #
    #     vLength = pLength(v)
    #     selfpos = self.getPos()  # type:tuple
    #     #如果t=0
    #     if t==0:
    #         t=-vLength/acc
    #     newPosx = selfpos[0] + v[0] * t + 1 / 2 * acc * t * t * v[0] / vLength
    #     newPosy = selfpos[1] + v[1] * t + 1 / 2 * acc * t * t * v[1] / vLength
    #
    #     distance=0
    #     reflectDire=None
    #     if isWallCollide:
    #         l = raycast(self.spaceID, wallLayer, selfpos, (newPosx, newPosy))
    #         if l:
    #             newPosx = l[0][0]
    #             newPosy = l[0][1]
    #             reflectDire=l[1]
    #             distance=wallCollideRadius
    #
    #     # if acc==0:
    #     #     self._originSyncHz=self.syncHz
    #     #     self.syncHz=0
    #     #     self.allClients.c_syncPos(self.getPos())
    #     #     self.c_straightMoveSpeed=v
    #
    #     self.moveToPointAcc((newPosx, newPosy), vLength, acc, distance,  isDirect, userData, isFace, False)
    #     return reflectDire

    #返回
    # def moveByDir(self, rad, distance, vLength, acc=0, userData=0, isFace=False, isWallCollide=False,
    #               wallLayer=0, wallCollideRadius=0):
    #
    #     selfpos = self.getPos()  # type:tuple
    #     endPos = pAdd(selfpos, pMult(radiansToVector2(rad), distance))
    #
    #     reflectDire = None
    #     endDis = 0
    #     if isWallCollide:
    #         l = raycast(self.spaceID, wallLayer, selfpos, endPos)
    #         if l:  #撞墙了
    #             if pIsZero(l[-1]):  #已经在墙壁里面了,那么应该往前挪一格,然后raycast
    #                 #这是一个bug,可能上次移动导致这次在墙壁里面
    #                 selfpos = pMoveToP(selfpos, endPos, 100)
    #                 if pEqual(selfpos, endPos):
    #                     pass
    #                 else:
    #                     l = raycast(self.spaceID, wallLayer, selfpos, endPos)
    #                     if l:
    #                         if pIsZero(l[-1]):  #仍旧在墙壁里面,那么不管了,直接移动吧,不管墙壁了
    #                             pass
    #                         else:  #移动了一格终于出来了
    #                             endPos = l[0]
    #                             reflectDire = l[1]
    #                             endDis = wallCollideRadius
    #             else:  #不在墙壁里,撞墙了
    #                 endPos = l[0]
    #                 reflectDire = l[1]
    #                 endDis = wallCollideRadius
    #         else:
    #             #并没有撞墙
    #             pass
    #
    #     self.moveToPointAcc(endPos, vLength, acc, endDis, False, userData, isFace, False)
    #     return reflectDire

    def moveByDir(self, rad, distance, vLength, acc=0, userData=0, isFace=False, isWallCollide=False,
                      wallLayer=0, wallCollideRadius=0):

        selfpos = self.getPos()  # type:tuple
        endPos = pAdd(selfpos, pMult(radiansToVector2(rad), distance))

        reflectDire = None
        endDis = 0
        if isWallCollide:
            l = raycast(self.spaceID,wallLayer, selfpos, endPos)
            if l:  #撞墙了
                endPos = l[0]
                reflectDire = l[1]
                endDis = wallCollideRadius
            else:
                #并没有撞墙
                pass

        self.moveId=self.moveToPointAcc(endPos, vLength, acc, endDis, False, userData, isFace, False)
        return reflectDire

    def navigateTo(self, destination, velocity, maxMoveDistance, maxSearchDistance, faceMovement, layer):
        self.stopMove()
        self.moveId=self.navigate(destination, velocity, maxMoveDistance, maxSearchDistance, faceMovement, layer)
        return self.moveId


    def logBody(self):
        return

    def stopMoveAndTurn(self):
        self.moveId=0
        self.cancelController("Movement")  #包含turn的controller

    def stopMove(self):
        self.emit(EVENTS.onStopMove)
        self.cancelController(self.moveId)
        self.moveId=0


    # def takeDamage(self,sender,type,num):
    #     pass

    # def onSimpleStore(self):
    #     pass

    # def onCollide(self, entity, distance, x, y):
    #     pass

    def onEnterTrap(self, entity, rangeXZ, rangeY, controllerID, userArg):
        pass

    def onLeaveTrap(self, entity, rangeXZ, rangeY, controllerID, userArg):
        pass

    # def onEnteredView(self, entity):
    #     pass

    def onMoveOver(self, controllerID, userData):
        pass

    # def onMove(self, controllerID, userData):
    #     pass

    # def onWitnessed(self, isWitnessed):
    #     pass

    def __________selfAllFuncs(self):
        pass

    def onMapThingDead(self):
        pass

    def __________endSelfAllFuncs(self):
        pass




    #p
    def tryDestroy(self):
        if self.isDestroying or self.isDestroyed:
            return
        self.isDestroying=True

        self.destroy()


    #太消耗了不弄
    # def cellOnStoreObj(self):
    #     MyCoroutine.closeAll(self)
    #     EventSystem.offAllEvent(self)
    #     Component.offAll(self)
    #     self.active=False

    def store(self):
        if not self.POOLOBJ:
            ERROR_MSG("store no POOL OBJ,do you want to tryDestroy?")
            return
        self.space.storeObj(self)


    def onStoreObj(self):
        pass

    def cellOnDestroy(self):
        MyCoroutine.corOnDestroy(self)
        EventSystem.offAllEvent(self)
        Component.offAll(self)
        if self.id in self.space.noPoolEns:
            del self.space.noPoolEns[self.id]
        self.space=None #type:SpaceCE


    def onTimer01s(self,tid):
        pass
    def onTimer1s(self,tid):
        pass
    """
    以trap代替View相关的方法
    """

    # def addTrapView(self, viewradius):
    #     self.addProximity(viewradius * 2, 0, TRAP_CAMP_view)

    # def onCallBack(self,cbNum):
    #     self.callbacks[cbNum]()
    #
    # def onCallBackM(self,cbNum,entityCall):
    #     self.callbacks[cbNum](entityCall)
