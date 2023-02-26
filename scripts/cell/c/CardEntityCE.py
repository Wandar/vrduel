# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2018 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2018-04-05 15:44
from __future__ import annotations
from KBEngine import *
from util import *
from c.ComponentCE import ComponentCE
from annos import *


"""
客户端表现以及动画

"""

WAITING_FOR_DESTROY_TIME=120 #等待2分钟再破坏,不可能有动画的时间长度超过2分钟

#monster cards or monsters
class CardEntityCE(ComponentCE):
    #c ALL UINT64
    c_duelID=0

    #c ALL CardData
    c_cardData=None #type:CardData

    #c ALL BOOL
    c_isWaitingForDestroy=False

    waitingForDestroyTime=0
    def onLoad(self):
        pass

    def initCardEntity(self,cardData):
        self.c_cardData=cardData



    def ___________________________anim(self):
        pass

    #c
    def playanimSyncCardData(self):
        self.allClients.playAnimSyncCardData()

    #c CardData
    def playanimSummon(self,cardData):
        self.allClients.playanimSummon(cardData)
        pass


    #c ID INT16
    def playanimAttack(self,enID,damage):
        self.allClients.playanimAttack(enID,damage)


    def ____________________________animend(self):
        pass

    """
    这张怪兽卡被破坏后,为什么要等待一段时间再破坏这个entity
    因为玩家间的动画效果长短不一,如果直接破坏,那么动画时间长的玩家的怪会突然消失
    """
    def setWaitingDestroy(self):
        self.c_cardData=CardData.getNone()
        self.c_isWaitingForDestroy=True
        self.waitingForDestroyTime=time.time()


    def checkDestroy(self):
        if time.time()-self.waitingForDestroyTime>WAITING_FOR_DESTROY_TIME:
            self.destroy()

    def tryDestroy(self):
        self.destroy()

    def onDestroy(self):
        pass