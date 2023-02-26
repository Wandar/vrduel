# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2017 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2017/9/13 3:31

from KBEngine import *

from c.ComponentCE import ComponentCE
from util import *


class NodeCE(ComponentCE):
    # noinspection PyMissingConstructor
    def __init__(self):
        self._initCellComponent()

    def onLoad(self):#只是一开始使用
        self._callAllComFunc("onLoad")

    def onTimerStart(self,tid):
        self._callAllComFunc("start")


    def onDestroy( self ):
        self._callAllComFunc("onDestroy")
        self.cellOnDestroy()


    #因为检查要一个个检查脚本实在太慢了,所以
    # def onCollide(self,entity,distance,x,y):
    #     self._callAllComFunc("onCollide",entity,distance,x,y)

    def onMoveOver(self, controllerID, userData):
        # if not pIsZero(self.c_straightMoveSpeed):
        #     self.syncHz=self._originSyncHz
        #     self.c_straightMoveSpeed=(0,0)
        #     self.allClients.c_syncPos(self.getPos())
        self.moveId=0
        self._callAllComFunc("onMoveOver",controllerID, userData)

    # def onMove(self, controllerID, userData):
    #     self._callAllComFunc("onMove",controllerID, userData)

    def onMoveFailure(self, controllerID, userData):
        # self._callAllComFunc("onMoveFailure",controllerID, userData)
        ERROR_MSG("onMoveFailure id=",self.id,self)
        self.onMoveOver(controllerID, userData)

    # def onEnteredView(self, entity):
    #     self._callAllComFunc("onEnteredView",entity)

    def onEnterTrap(self, entity, rangeXZ, rangeY, controllerID, userArg):
        self._callAllComFunc("onEnterTrap",entity, rangeXZ, rangeY, controllerID, userArg)

    def onLeaveTrap(self, entity, rangeXZ, rangeY, controllerID, userArg):
        self._callAllComFunc("onLeaveTrap",entity, rangeXZ, rangeY, controllerID, userArg)

    def onStoreObj(self):
        self.active=False
        self._callAllComFunc("onStoreObj")

    # def onWitnessed(self, isWitnessed):
        # self._callAllComFunc("onWitnessed",isWitnessed)
        # DEBUG_MSG("witness ",isWitnessed)


    def onReinit(self):
        self._callAllComFunc("onReinit")


