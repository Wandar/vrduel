# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2018 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2018-04-04 3:18
from __future__ import annotations
from KBEngine import *


from Duel import Duel
from annos import *
from c.space.SpaceComponentCE import SpaceComponentCE
from mydicts import mySpaces
from util import *


"""
class SPACE_TYPE(MyEnum):
    voidspace=0
        空场景,等待时
    home=1
        家
    tutorial=2
        教程场景
    debug=3
        debug场景
    mpublic=4
        开放的房间
    mprivate=5
        私人房间
    matchmaking=6
        匹配的房间

"""


"""
duel place
"""
FRONT_DISTANCE=3 #3米
SIDE_DISTANCE=3


class SpaceCE(SpaceComponentCE):
    createTime=0
    genNums=None


    fastTimerTid=0

    timer1sTid=0
    timer1sNoENCnt=0
    timer1sEns=None

    #c CELL ID
    cell_roomID=0 #public roomID,maybe 0
    #c CELL UINT8
    cell_spaceType=0 #SPACE_TYPE


    duels=None
    startPosList=[]



    ###############voice
    voiceAddress=""
    voiceRoomName=""


    #####################

    def onLoad(self):
        if 0: self.base = self.base  #type:SpaceBA
        self.createTime=time.time()

        # self.timer01sEns={}
        self.timer1sEns={}
        self.startPosList=[]
        self.duels={} #type:Dict[int,Duel]

        setSpaceData(self.spaceID,"roomID",str(self.cell_roomID))
        setSpaceData(self.spaceID,"spaceType",str(self.cell_spaceType))

        # self.initVoiceRoom()

        self.setInterval(3,3,self.onSpaceTimer)


    def start(self):
        if self.cell_spaceType==SPACE_TYPE.home:
            self.testSpaceFunc()


    def onAvatarEnter(self, avatar:AvatarCE):
        self.avatars[avatar.id]=avatar
        avatar.c_voiceRoomName=self.voiceRoomName
        avatar.c_voiceAddress=self.voiceAddress



    def onAvatarDestroy(self, avatar):
        if avatar.id in self.avatars:
            del self.avatars[avatar.id]
        else:
            WARNING_MSG("onAvaDestroy not has avatar ",avatar.id)



    def testSpaceFunc(self):
        cvec3.set(-6.5,0,-3)
        a=createEntity("Avatar",self.spaceID,cvec3,cvec3Zero,{"c_isNPC":True}) #type:AvatarCE
        cvec3.set(-6,0,-7)
        createEntity("TestObject",self.spaceID,cvec3,cvec3Zero)



    def _____________________________________timerfunc(self):
        pass

    #节省性能,某些闲置的房间就不开了
    def setFastTimerEnabled(self, isEnabled):
        if isEnabled:
            if not self.fastTimerTid:
                self.fastTimerTid=self.setInterval(1 / 15, 1 / 15, self.onFastTimer)
        else:
            if self.fastTimerTid:
                self.delInterval(self.fastTimerTid)
                self.fastTimerTid=0


    def onFastTimer(self, tid):
        for duelID,duel in self.duels.items():
            duel.update01s()
        if len(self.duels)==0:
            self.setFastTimerEnabled(False)


    def onSpaceTimer(self,tid):
        self.base.updatePlayerCnt(len(self.avatars))


    # def add01sTimer(self,en):
    #     if not self.timer01sTid:
    #         self.timer01sTid=self.setInterval(0.1,0.1,self.onSpace01sTimer)
    #     self.timer01sEns[en.id]=en
    #
    # def remove01sTimer(self,en):
    #     if en.id in self.timer01sEns:
    #         del self.timer01sEns[en.id]


    # def add1sTimer(self,en):
    #     if not self.timer1sTid:
    #         self.timer1sTid=self.setInterval(0.1,0.1,self.onSpace1sTimer)
    #     self.timer1sEns[en.id]=en
    #
    # def remove1sTimer(self,en):
    #     if en.id in self.timer1sEns:
    #         del self.timer1sEns[en.id]
    #
    # def onSpace1sTimer(self,tid):
    #     for id,en in self.timer1sEns.items():
    #         en.update1s(tid)
    #     if not len(self.timer1sEns):
    #         self.timer1sNoENCnt+=1
    #         if self.timer1sNoENCnt>100:
    #             self.timer1sNoENCnt=0
    #             self.delInterval(self.timer1sTid)
    #             self.timer1sTid=0
    #     else:
    #         self.timer1sNoENCnt=0


    def _______________________________________endtimerfunc(self):
        pass

    def _____________________________________________________________duelfunc(self):
        pass


    _cardUniCnt=0
    def genCardUniID(self):
        self._cardUniCnt+=1
        return self._cardUniCnt


    def tryStartDuelWithBot(self,starterID,duelPlaceData:DuelPlace):

        #check illegal
        INFO_MSG("req start DuelWith bot ",starterID)
        if starterID not in entities:
            return

        starter=entities[starterID] #type:AvatarCE
        if starter.className!="Avatar":
            return


        if not self._checkDuelPlaceID(duelPlaceData.placeID):
            WARNING_MSG("place ID already")
            return

        success=SUCCESS
        if starter.c_duelID:
            WARNING_MSG("already in duel")
            success=FAIL

        if not starter.checkCurrentDeckLegal():
            success=FAIL_DECK_ILLEGAL
            #TODO notify

        if success!=SUCCESS:
            return

        INFO_MSG("startDuel success")

        #create bot and start duel

    def tryStartDuel(self,starterID,receiverID,duelPlaceData:DuelPlace):
        """
        客户端寻找场地信息
        上传duel的场地信息
        创建duel类

        玩家变到duel的位置
        showLabel
        抽手牌

        :return:
        """

        #check illegal
        INFO_MSG("req start Duel ",starterID,receiverID)
        if starterID not in entities:
            return
        if receiverID not in entities:
            return

        starter=entities[starterID] #type:AvatarCE
        if starter.className!="Avatar":
            return
        receiver=entities[receiverID] #type:AvatarCE
        if receiver.className!="Avatar":
            return



        if not self._checkDuelPlaceID(duelPlaceData.placeID):
            WARNING_MSG("place ID already")
            return

        success=SUCCESS
        if starter.c_duelID or receiver.c_duelID:
            WARNING_MSG("already in duel")
            success=FAIL

        if starter.checkCurrentDeckLegal()==False or receiver.checkCurrentDeckLegal()==False:
            success=FAIL_DECK_ILLEGAL
            #TODO notify

        if success!=SUCCESS:
            return

        INFO_MSG("startDuel success")

        #全部没问题,开始决斗


        duelID=genUUID64()
        starter.c_duelID=duelID
        receiver.c_duelID=duelID

        if starter.c_isNPC:
            starter.npcOriginPos=Vector3(starter.position)
        if receiver.c_isNPC:
            receiver.npcOriginPos=Vector3(receiver.position)

        #设置玩家的位置和朝向
        ds1=starter.position.flatDistSqrTo(duelPlaceData.p1)
        ds2=starter.position.flatDistSqrTo(duelPlaceData.p2)
        if ds1<ds2:
            starter.position=duelPlaceData.p1
            receiver.position=duelPlaceData.p2
        else:
            starter.position=duelPlaceData.p2
            receiver.position=duelPlaceData.p1
        rad=vec3FaceTo(starter.position,receiver.position)
        starter.direction=Vector3(0,rad,0)
        rad=vec3FaceTo(receiver.position,starter.position)
        starter.direction=Vector3(0,rad,0)



        #开启墙壁
        starter.resetDuelArgs()
        receiver.resetDuelArgs()
        starter.c_currentDuelPlaceID=duelPlaceData.placeID
        receiver.c_currentDuelPlaceID=duelPlaceData.placeID


        starter.c_showLabel("startDuel")
        receiver.c_showLabel("startDuel")

        self.setFastTimerEnabled(True)
        self.duels[duelID]=Duel(self,duelID,duelPlaceData,[starter,receiver])
        self.duels[duelID].startGame()


    def _checkDuelPlaceID(self,placeID):
        for duelID,duel in self.duels.items():
            if duel.duelPlaceData.placeID==placeID:
                return False
        return True

    def stopDuel(self,duelID):
        if duelID not in self.duels:
            ERROR_MSG("cisyudcbudcy")
            return
        duel=self.duels[duelID]
        for ID,avatarCE in duel.avatars.items():
            if avatarCE.isDestroyed:
                continue
            avatarCE.c_duelID=0
            avatarCE.c_currentDuelPlaceID=0
            avatarCE.c_ID=0
            avatarCE.resetDuelArgs()
            avatarCE.c_stopDuel()
            avatarCE.c_showLabel("duelstop")
            if avatarCE.c_isNPC and avatarCE.npcOriginPos:
                avatarCE.setPos(avatarCE.npcOriginPos)

        duel.destroyGame()
        del self.duels[duelID]
        #TODO
        #如果是npc,直接破坏,如果是玩家不管


    def _____________________________________________________________duelfuncend(self):
        pass






    def _________________________________________________voice(self):
        pass


    def initVoiceRoom(self):
        self.voiceAddress=""
        self.voiceRoomName=str(number64toStr(genUUID64()))
        if isDebugVer():
            return

        if self.cell_spaceType in (SPACE_TYPE.mpublic,SPACE_TYPE.matchmaking,SPACE_TYPE.debug):
            globalData["VoiceManagerBA"].reqFreeVoiceAddress(self)
            self.setInterval(30,30,self.onTimerVoice)

    #p STRING
    def onReqFreeVoiceAddress(self,address):
        self.voiceAddress=address
        for id,avatar in self.avatars.items():
            avatar.c_voiceRoomName=self.voiceRoomName
            avatar.c_voiceAddress=self.voiceAddress


    def onTimerVoice(self,tid):
        if self.voiceAddress:
            globalData["VoiceManagerBA"].sendVoiceAddressPlayerCnt(self.id,self.voiceAddress,len(self.avatars))


    def ______________________________________________endvoice(self):
        pass


    def getSameCoreSpaces(self):
        results=[]
        for spaceID,space in mySpaces.items():
            space=space #type:SpaceCE
            if spaceID==self.spaceID:
                continue
            if not space.cell_roomID:
                continue
            if space.isDestroyed or space.isDestroying:
                continue
            if time.time()-space.createTime<0.5:
                continue
            if space.cell_spaceType != SPACE_TYPE.mpublic:
                continue
            results.append(space)

        #TODO 还是有风险,比如base正在破坏
        return results


    def logEntityNum(self):
        d={
            "stored":0,
            "inSpace":0
        }
        for id,en in entities.items():
            if en.spaceID !=self.spaceID:
                continue
            if en.getPos()[0]<0:
                d["stored"]+=1
            else:
                d["inSpace"]+=1
        return d



    #p
    def tryDestroy(self):
        if self.isDestroying or self.isDestroyed:
            return
        if self.voiceAddress:
            globalData["VoiceManagerBA"].delVoiceAddressPlayerCnt(self.id,self.voiceAddress)
        self.isDestroying=True
        for id,en in entities.items():
            if en.spaceID==self.spaceID and en.id!=self.id:
                en.destroy()

        delSpaceData(self.spaceID,"roomID")
        delSpaceData(self.spaceID,"spaceType")

        self.destroy()

    # def onTimerTryDestroy(self,tid):
    #     self.destroy()

    def onDestroy(self):
        pass
