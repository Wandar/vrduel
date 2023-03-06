# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2018 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2018-04-05 15:44
from __future__ import annotations
from KBEngine import *
from c.ComponentCE import ComponentCE
from util import *
from annos import *


class Anim:
    startTime = 0
    func = None
    animID = 0

    def __init__(self, id, f):
        self.animID = id
        self.func = f
        pass

    def startAnim(self):
        self.startTime = time.time()
        self.func()


class AvatarCE(ComponentCE):
    #c ALL BOOL
    c_isNPC = False

    npcOriginPos=None



    #c OWN STORE_DECK_DATA
    c_currentDeck = None

    deckNoDuel = None  #非决斗时使用的deck类,数组



    ####################################外表
    #c ALL UNICODE
    c_nickName=""
    #c ALL ID
    c_lHandID=0
    #c ALL ID
    c_rHandID=0


    #######################################mainuipanel
    cardPages=None  #[[cardData,cardData],[cardData,cardData],...]每一页
    #c OWN STRING
    c_uniIDstr=""
    #c ALL UINT64 STORED
    c_coin=0
    #c ALL UINT64 STORED
    c_bcrystal=0
    #c ALL UINT64 STORED
    c_wcrystal=0

    #TODO 头像,个性签名,等级经验





    ####################决斗相关

    #c OWN LIST_BannerData
    c_bannerList = []


    #c ALL UINT64
    c_duelID = 0 #如果不为0就是在决斗
    #c OWN UINT8
    c_currentDuelPlaceID=0 #如果正在决斗,当前正在使用的duelPlace的ID

    #c OWN LIST_UINT64
    c_watchDuelIDList=[]



    ####################玩家自身看到的
    #c OWN ID
    c_roomID=0 #player seen roomID,maybe 0
    #c OWN INT8
    c_panelSyncType=0 #手牌panel当前显示 墓地,除外,或是额外
    #c OWN BOOL
    c_graveCanUse=False #墓地有卡可发动
    #c OWN BOOL
    c_bdeckCanUse=False
    #c OWN BOOL
    c_banishedCanUse=False

    #c OWN LIST_ENID_TO_CARDDATA
    # c_enIDToCardDataList=[] #用来隐藏覆盖卡的数据,暂时不使用

    ################玩家和其他人看到的

    #c ALL UINT16
    c_handCardNum = 0 #手卡数量
    #c ALL UINT16
    c_deckNum = 0 #卡组卡牌数量
    #c ALL UINT8
    c_bdeckNum=0 #额外卡组数量
    #c ALL UINT8
    c_coverSpellNum=0 #覆盖的卡数量
    #c ALL UINT16
    c_LP = 0
    #c ALL UINT8
    c_EP = 0
    #c ALL INT8
    c_camp = 0  #哪边的
    #c ALL CardData
    c_grabCard=None
    #c ALL BOOL
    c_isSummoning=False #设置为true
    #c OWN CardData
    c_summoningCard=None

    ###################################






    ######################################voice
    #c OWN STRING
    c_voiceAddress="" #ip:port
    #c OWN STRING
    c_voiceRoomName=""

    #c ALL STRING
    c_voicePlayerName="" #客户端发送过来的




    ###################################





    ############################################

    def onLoad(self):
        if 0: self.base = self.base  #type:AvatarBA
        self.topSpeed = 0
        self.topSpeedY = 0

        self.c_roomID=self.space.cell_roomID


        self.c_bannerList = []

        self.deckNoDuel = []





    def onGetWitness(self):
        #可能不会进入这个函数?
        #触发要早于start
        INFO_MSG("avatar onGetWitness")
        self.setViewRadius(200,5)


    def start(self):
        DEBUG_MSG("create Avatar cell")

        self.testInit()
        pass





    def testInit(self):
        d = {
            "name":"testDeck",
            "data":""
        }
        j = {"a": [], "b": [], "c": [], "side": []}
        for i in range(40):
            j["a"].append(300)
        d["data"] = json.dumps(j)

        self.c_currentDeck = d


    #e
    def e_onClientConnect(self):
        INFO_MSG("client connect to avaCE")
        #client重连

        ASSERT_MSG(self.client!=None,"client reconnect no found client")
        if self.c_duelID:
            #同步决斗数据,一些重要数据重新下发
            #包括手牌,是否正在召唤
            self.c_showLabel("reconnectduel")
            duel=self.getDuel()
            pass


    #e
    def e_testClickCard(self):
        self.c_testClickCard()
        pass

    #c
    def c_testClickCard(self):
        if self.client: self.client.c_testClickCard()
        pass

    #
    #
    # def pushAnim(self,func):
    #     isPlaying=self.isAnimPlaying()
    #     self.animSeq.append(Anim(self.genAnimID(), func))
    #
    #     if not isPlaying:
    #         self._playNextAnim()
    #
    #
    # def _playNextAnim(self):
    #     anim=self.animSeq[0]
    #     anim.startAnim()
    #
    #
    # def isAnimPlaying(self):
    #     return len(self.animSeq)>0
    #
    # def onAnimEnd(self,animID):
    #     #检察id
    #     if len(self.animSeq):
    #         #暂时只有单线动画
    #         if animID!=self.animSeq[0].animID:
    #             ERROR_MSG("animEnd animID not equal",animID,self.animSeq[0].animID)
    #         self.animSeq.pop(0)
    #
    #     if len(self.animSeq):
    #         self._playNextAnim()

    # def checkAnimOverTime(self):
    #     #检察动画是否超时了
    #     ANIM_OVER_TIME=30
    #     if len(self.animSeq):
    #         if time.time()-self.animSeq[0].startTime>ANIM_OVER_TIME:
    #             ERROR_MSG("anim over time")
    #             #强制结束动画

    def resetDuelArgs(self):
        # self.c_enIDToCardDataList=[]
        self.syncHandCard([],True)
        pass



    def receiveDeckData(self, deckData):
        self.c_currentDeck = deckData



    #e LIST_VECTOR3
    def e_setStartPoses(self, vList):
        INFO_MSG("setStartPoses ", vList)
        self.space.startPosList = vList




    def ______________________________________________handfunc(self):
        pass

    #e VECTOR3 VECTOR3 VECTOR3 VECTOR3
    def e_createHands(self,leftPos,leftRot,rightPos,rightRot):
        if not self.c_lHandID:
            a=self.space.objMgrCE.getStoredObj("Hand")
            self.c_lHandID=a.id

        if not self.c_rHandID:
            b=self.space.objMgrCE.getStoredObj("Hand")
            self.c_rHandID=b.id

        leftHand=entities[self.c_lHandID]
        leftHand.c_order=0
        leftHand.setPos(leftPos)
        leftHand.setRad(leftRot)
        leftHand.controlledBy=self.base

        rightHand=entities[self.c_rHandID]
        rightHand.c_order=1
        rightHand.setPos(rightPos)
        rightHand.setRad(rightRot)
        rightHand.controlledBy=self.base


    def logHandPos(self):
        leftHand=entities[self.c_lHandID]
        rightHand=entities[self.c_rHandID]
        DEBUG_MSG("l pos="+vec3ToStr(leftHand.getPos())+" r pos="+vec3ToStr(rightHand.getPos()))


    def ______________________________________________handfuncend(self):
        pass


    def _______________________________________________funcNotInduel(self):
        pass


    #e ID
    def e_reqAvatarInfo(self, id):
        pass

    #c
    def c_onReqAvatarInfo(self):
        if self.client: self.client.c_onReqAvatarInfo()

    #e ID DuelPlace
    def e_reqDuel(self, avatarID, duelPlaceData):
        if not self.checkTime("e_reqDuel", 1):
            return

        # self.space.
        if not checkIsClass(avatarID, "Avatar"):
            return

        en = entities[avatarID]  #type:AvatarCE
        if en.c_duelID or self.c_duelID:
            self.c_showBannerNOCB("", "alreadyInDuel")
            return
        if en.c_isNPC:
            self.space.tryStartDuel(self.id, en.id, duelPlaceData)
        else:
            ERROR_MSG("iusdyvcbsuydc")
        #TODO other player


    # def onReqDuel(self,avatarCE,YesOrNo):
    #     if not YesOrNo:
    #         return
    #     self.space.startDuel()


    def checkCurrentDeckLegal(self):
        if not self.c_currentDeck:
            return False

        j=json.loads(self.c_currentDeck["data"])

        if len(j["a"])<=0 or len(j["a"])>=60:
            return False
        if len(j["b"])>=15:
            return False

        #TODO 检察重复卡的数量
        for cardID in j["a"]:
            cardID=int(cardID)
            # cardData=CardData.genSimple(cardID,self.Game.duel.spaceCE.genUniID())

        for cardID in j["b"]:
            cardID=int(cardID)
            # cardData=CardData.genSimple(cardID,self.Game.duel.spaceCE.genUniID())

        for cardID in j["c"]:
            cardID=int(cardID)
            # cardData=CardData.genSimple(cardID,self.Game.duel.spaceCE.genUniID())

        return True

    def ________________________________________________funcNotInDuelEnd(self):
        pass

    def ________________________________________________funcInDuel(self):
        pass



    """
    
    同步游戏
        手牌,使用抽卡动画以及回合结束时同步一下以防万一
        卡组,不同步,只有张数
        墓地,除外,额外:需要再同步
        场上的卡,使用CardEntity,建立和销毁
        血量和能量
    """


    def e_reqSyncDuel(self):
        """
        客户端退出后重连,需要搞定的


        :return:
        """
        pass

    def setDeckNum(self,num:int):
        self.c_deckNum=num

    def syncHandCard(self,l,isAnim=True):
        self.c_handCardNum=len(l)
        self._c_syncHandCard(l,isAnim)

    #c LIST_CardData BOOL
    def _c_syncHandCard(self,l,isAnim):
        if self.client: self.client._c_syncHandCard(l,isAnim)


    # def syncGameToClient(self):
    #     duel=self.space.duels[self.c_duelID]
    #     ID=self.c_ID
    #     game=duel.Game
    #     game.Hand_Deck.hands[ID]
    #     len(game.Hand_Deck.decks[ID])
    #     game.minions
    #     game.spells

    # _bdeckSyncDirty=True
    #请求同步GY or banished or Bdeck
    #e INT8
    def e_reqSyncPanel(self,state):
        self.c_panelSyncType=state
        if state==PANEL_SYNC_TYPE.handcard:
            pass
        elif state==PANEL_SYNC_TYPE.bdeck:
            #不管怎样都传输
            pass

            # if self._bdeckSyncDirty:
            #     self._bdeckSyncDirty=False #should sync
            # else:
            #     pass


    #Game调用
    def checkSyncPanel(self,state:PANEL_SYNC_TYPE):
        #只有玩家看着墓地的时候才会同步
        if state!=self.c_panelSyncType:
            return


    #c INT8 ID_LIST_CardData
    def c_syncPanel(self, INT8,dlist):
        if self.client:self.client.c_syncPanel(INT8,dlist)




    #用于本玩家得知场上覆盖的自己的卡是什么,暂时不需要做得这么完善
    # def updateEnidToCardData(self,enID,cardData):
    #     for i in range(len(self.c_enIDToCardDataList)-1,-1,-1):
    #         t=self.c_enIDToCardDataList[i]
    #         if t['id']==enID:
    #             del self.c_enIDToCardDataList[i]
    #
    #     self.c_enIDToCardDataList.append({"id":enID,'cardData':cardData})
    #     self.c_enIDToCardDataList=self.c_enIDToCardDataList
    #
    # def removeEnIDToCardData(self,enID):
    #     for i in range(len(self.c_enIDToCardDataList)-1,-1,-1):
    #         t=self.c_enIDToCardDataList[i]
    #         if t['id']==enID:
    #             del self.c_enIDToCardDataList[i]
    #     self.c_enIDToCardDataList=self.c_enIDToCardDataList

    def getDuel(self)->Duel:
        if not self.c_duelID:
            return None
        if self.c_duelID not in self.space.duels:
            return None
        return self.space.duels[self.c_duelID]



    ####################################这是从客户端发过来的
    #e ID STRING
    def e_resolveMove(self,cardUniID,step):
        duel=self.getDuel()
        if not duel:
            return
        duel.resolveMove(self.c_camp,cardUniID,step)



    #e UINT64 BOOL
    def e_setWatchDuel(self,duelID,isWatching):

        #如果成功观看,那么sync所有
        pass


    #e
    def e_summon(self):
        self.c_isSummoning=False
        self.getDuel().resolveMove(self.c_camp,)




    def _________________________________________________endfuncInDuel(self):
        pass



    def __________________________________________clientoperate(self):
        pass


    #e UINT8
    def e_controllerOperate(self,controllerbind):
        if self.c_duelID:
            self.controllerOperateInDuel(controllerbind)
        else:
            self.controllerOperateNotInDuel(controllerbind)



    def controllerOperateInDuel(self,controllerbind):
        if controllerbind==VR_CONTROLLER.RightTrigger:
            pass



    def controllerOperateNotInDuel(self,controllerbind):
        if controllerbind==VR_CONTROLLER.RightTrigger:
            #programmed by client
            pass


    #e CardData VECTOR3
    def e_summonMonster(self,card:CardData,pos):
        #获取秘钥
        pass

    #e CardData
    def c_onSummonMonster(self,card,pos):
        pass



    def _______________________________________clientoperateEnd(self):
        pass



    def _______________________________________________duelanims(self):
        pass

    #c UINT16
    def playanim(self,animType):
        self.allClients.playanim(animType)

    #c UINT16
    def playanimSelf(self,animType):
        if self.client:self.client.playanimSelf(animType)

    #c INT8
    def playanimTurnStart(self,camp):
        if self.client:self.client.playanimTurnStart(camp)

    def playanimDraw1Card(self, card):
        self.mc_playanimDraw1Card(card)


    #c UINT8 UINT8
    def playanimToPhase(self,side,phase):
        if self.client:self.client.playanimToPhase(side,phase)

    #c CardData
    def mc_playanimDraw1Card(self,card):
        self.allClients.mc_playanimDraw1Card(card)
        #TODO 改成本机和其他机器不同,防止手牌泄露


    #c ANID ID
    def playanimCardReturnToHand(self, entityID):
        self.allClients.playCardReturnToHand(anid, entityID)


    def playanimCardReturnToDeck(self):
        pass

        self.allClients.playanimSummon

    def playanimCardReturnToGY(self):
        pass



    def ___________________________________________________________endduelanims(self):
        pass











    def ___________________________________________clientNotify(self):
        pass

    """
    客户端提醒,有几种:
    直接提示一行字,可以消去
    浮动出现一行字,一段时间后消失
    横向移动一行字
    OK banner不带回调
    出现OK banner带回调
    出现YesNo banner
    
    
    
    决斗相关:
    投色子决定先后攻
    卡牌选择器
    
    """

    #c STRING STRING
    def c_showLabelStatic(self, key, label): #显示静止不动的label
        if self.client: self.client.c_showLabelStatic(key, label)

    #c STRING
    def c_hideLabelStatic(self, key):
        if self.client: self.client.c_hideLabelStatic(key)

    #c
    def c_hideAllLabelStatic(self):
        if self.client: self.client.c_hideAllLabelStatic()

    #c STRING
    def c_showLabel(self, STRING): #显示一个label
        if self.client: self.client.c_showLabel(STRING)

    #c STRING STRING
    def c_showBannerNOCB(self, title, text):  #没有返回值
        if self.client: self.client.c_showBannerNOCB(title, text)

    def showBannerWithOK(self, title, text, cb: str):
        self.showBanner(title, text, ["OK"], cb)
        pass

    def showBannerYesOrNo(self, title, text, cb):
        self.showBanner(title, text, ["YES", "NO"], cb)
        pass

    def showBanner(self, title, text, options: [str], cb: str):
        if self.c_isNPC:
            return
        """
        带返回值的banner
        :param title:
        :param text:
        :return:
        """
        if title == None or title == "":
            ERROR_MSG("must has title")
            return

        for b in self.c_bannerList:
            if b.title == title:
                WARNING_MSG("showBanner chongfu ", title)
                return

        b = BannerData()
        b.title = title
        b.text = text
        b.options = options
        b.cb = cb
        self.c_bannerList.append(b)
        self.c_bannerList = self.c_bannerList

    #e STRING STRING UINT8
    def e_onBanner(self, title, cb, result):
        self._removeBanner(title)
        cbfunc = getattr(self, cb, None)
        if cbfunc:
            cbfunc(result)
        else:
            ERROR_MSG("e_onBanner not found ", cb)

    #客户端点击后会自动消除,增加这个主要是如果客户端断线重连应该重新显示banner
    def _removeBanner(self, title):
        for i in range(len(self.c_bannerList) - 1, -1, -1):
            if self.c_bannerList[i].title == title:
                del self.c_bannerList[i]
        self.c_bannerList = self.c_bannerList

    def ________________________________________endclientNotify(self):
        pass



    def ____________________________________________mainpanel(self):pass


    #e UINT8
    def e_reqDuelWithBot(self,num):

        pass



    def ____________________________________________mainpanelEnd(self):pass



    def ____________________________________________voice(self):
        pass

    #TODO 设置开口说话标志

    #e STRING
    def e_setVoicePlayerName(self,n):
        self.c_voicePlayerName=n




    def _________________________________________endvoice(self):
        pass


    #p
    def onClientDeathCell(self):
        INFO_MSG("client death cell")



    def tryDestroy(self):
        if self.isDestroyed or self.isDestroying:
            return
        self.isDestroying=True

        if self.c_duelID:
             self.space.stopDuel(self.c_duelID)

        if self.c_lHandID in entities:
            entities[self.c_lHandID].store()
        if self.c_rHandID in entities:
            entities[self.c_rHandID].store()
        self.destroy()
        pass

    def onDestroy(self):
        # self.testObj.destroy()
        pass
