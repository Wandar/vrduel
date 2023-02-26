# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2018 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2018-04-02 3:52
from __future__ import annotations
from KBEngine import *

from c.space.SpaceComponentBA import SpaceComponentBA
from util import *
from annos import *

"""
空间种类:
    玩家的家
    决斗大厅
    野外闯关关卡

"""


class SpaceBA(SpaceComponentBA):
    #c BASE UINT8
    spaceType = 0
    #c BASE ID
    roomID = 0  #used to join public rooms,if player's home or idle room,this is 0
    #c BASE CALL
    owner = None  #type:AccountBA
    #c BASE STRING
    sceneName = ""  #代表场景的bundle名称,例子如果是HomeScene那就是本包包含的场景,如果是HomeScene/HomeScene那就说明是HomeScene的assetbundle包里面的HomeScene场景
    #c BASE UNICODE
    spaceName = ""  #玩家设置的空间名称
    #c BASE STRING
    password=""
    #c BASE STRING
    lan="en" #房间使用的语言
    state = SPACE_STATE.creating


    avatarWaitToLogin=None #目前只有idlescene用到


    def onLoad(self):
        if 0: self.cell = self.cell  #type:Space


        ASSERT_MSG(self.sceneName != "", "space no sceneName")

        if self.roomID:
            self.cellData["cell_roomID"] = self.roomID
        self.cellData["cell_spaceType"] = self.spaceType
        if self.spaceType!=SPACE_TYPE.idle: #idle space delay create
            self.createCellEntityInNewSpace(0)


    def start(self):
        pass



    def onGetCell(self):
        self.state = SPACE_STATE.normal

        if self.spaceType==SPACE_TYPE.idle:
            if self.avatarWaitToLogin:
                self.avatarWaitToLogin.onLoginToSpace(SUCCESS, self.cell, self.sceneName,self.spaceType)
                self.avatarWaitToLogin=None

        if self.roomID:
            baseAppData["space_" + str(self.roomID)] = {"mail": self,
                                                        "sceneName": self.sceneName,
                                                        "spaceName": self.spaceName,
                                                        "createTime":time.time(),
                                                        "roomID":self.roomID,
                                                        "lan":"en",
                                                        "password":self.password,
                                                        "playerZeroTime":time.time()
                                                        }
            baseAppData["p_" + str(self.roomID)] = 0

    def onLoseCell(self):
        if self.state==SPACE_STATE.trydestroying:
            return
        self.state=SPACE_STATE.initing

    def onCellCrash(self):
        if self.spaceType == SPACE_TYPE.home:
            return

        ERROR_MSG("space cell crash ,id=%d"%self.id)
        if self.roomID:
            getSpaceManagerBA().onSpaceDestroy(self.roomID)

        if self.spaceType == SPACE_TYPE.mpublic:
            #delete space info and playercnt info
            k = "space_" + str(self.roomID)
            kp = "p_" + str(self.roomID)
            if k in baseAppData:
                del baseAppData[k]
            if kp in baseAppData:
                del baseAppData[kp]

        self.state = SPACE_STATE.trydestroying
        self.delayDestroy()

    #p CALL
    def avatarLogin(self, avatarBA):
        if self.isDestroying or self.isDestroyed:
            WARNING_MSG("join space is destroying")
            avatarBA.onLoginToSpace(FAIL,self,self.sceneName,self.spaceType)
            return

        if self.spaceType==SPACE_TYPE.idle:
            if not self.cell:
                self.createCellEntityInNewSpace(0)
                self.avatarWaitToLogin=avatarBA
                return

        if not self.cell:
            ERROR_MSG("login to space no cell")
            avatarBA.onLoginToSpace(FAIL,self,self.sceneName,self.spaceType)
            return

        if self.state == SPACE_STATE.normal:
            avatarBA.onLoginToSpace(SUCCESS, self.cell, self.sceneName,self.spaceType)
        else:
            avatarBA.onLoginToSpace(FAIL, self, self.sceneName,self.spaceType)

    #p UINT16
    def updatePlayerCnt(self, playerCnt):
        if self.isDestroying or self.isDestroyed:
            return
        key = "p_" + str(self.roomID)
        if key not in baseAppData:
            return
        p = baseAppData[key]
        if p != playerCnt:
            baseAppData[key] = playerCnt
            # if playerCnt==0:
            #     j=baseAppData["space_" + str(self.roomID)]
            #     j["playerZeroTime"]=time.time()
            #     baseAppData["space_" + str(self.roomID)]=j



    #p
    def tryDestroy(self):
        if self.isDestroying or self.isDestroyed:
            return
        self.isDestroying = True

        if self.roomID:
            getSpaceManagerBA().onSpaceDestroy(self.roomID)

        if self.spaceType == SPACE_TYPE.mpublic:
            #delete space info and playercnt info
            k = "space_" + str(self.roomID)
            kp = "p_" + str(self.roomID)
            if k in baseAppData:
                del baseAppData[k]
            if kp in baseAppData:
                del baseAppData[kp]

        self.state = SPACE_STATE.trydestroying
        if self.cell:
            self.cell.tryDestroy()

    def onDestroy(self):
        pass
