# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2018 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2018-04-05 15:44
from __future__ import annotations

import sys

from KBEngine import *

from c.ProxyBA import ProxyBA
from util import *
from annos import *

try:
    sys.path.append(os.getenv("curpath")+"/sec")
    from script import AccountFunc
except:
    pass

"""
进入后创建一个个人的space,可以进行pve


玩家功能:
    
    
    
    Avatar
        组牌
        买卡
        回家
        进pve房间
        进大厅房间
        匹配
    
    Account
        

"""


class VoiceData:
    ip = ""
    port = 0
    voiceRoomID = 0


class AvatarBA(ProxyBA):
    account = None  #type:AccountBA
    accountFunc=None #type:AccountFunc

    ######################client ui
    #c OWN UINT32
    _c_energy=0




    #################################

    #busy时不破坏不响应玩家操作,暂时不使用
    busy = None  #type:Busy

    sceneName = "" #如果为空,就是在IdleScene
    createCellTime = 0

    def onLoad(self):
        if 0: self.cell = self.cell  #type:AvatarCE
        self.busy = Busy(0)
        pass

    def initAvatar(self, accountBA:AccountBA):
        self.account = accountBA
        self.__ACCOUNT_NAME__=accountBA.__ACCOUNT_NAME__
        self.__ACCOUNT_PASSWORD__=accountBA.__ACCOUNT_PASSWORD__
        #cell data
        self.cellData["c_uniIDstr"]=accountBA.uniIDstr
        self.cellData["c_nickName"]=accountBA.nickName
        self.cellData["c_coin"]=accountBA.coin
        self.cellData["c_bcrystal"]=accountBA.bcrystal
        self.cellData["c_wcrystal"]=accountBA.wcrystal

        if not isDebugVer():
            self.accountFunc=AccountFunc.AccountFunc(self,self.account)


    def onClientEnabled(self):
        if self.hasAnyCoroutine() or self.hasAnyLock():
            ERROR_MSG("avatar login with")
            self.tryDestroy()
            return

        if not self.cell:
            self.showBannerOKBaseCB("", "login success", "onClientLoginClickOK")

    #玩家点击了OK
    def onClientLoginClickOK(self, r):
        self.tryToLoginToSpace(self.account.myHome)


    def testSendCardData(self):
        #发送给客户端一次不能超过65535字节,简单的数据差不多10000张卡
        # l=[]
        # for i in range(10000):
        #     a=CardData({
        #         "id":i,
        #         "uniID":0,
        #         "entityID":0,
        #         "mana":0,
        #         "attack":0,
        #         "defense":0,
        #         "health":0,
        #     })
        #     l.append(a)

        l = []
        for i in range(50):
            a = {
                "i": i * 100,
                "n": 0,
            }
            l.append(a)

        self.c_testSendCardData(l)


    #下发拥有的卡牌到客户端,客户端会叠加
    def syncOwnedCardsToClient(self, l):
        if not self.client:
            return
        l = []
        for i in range(10000):
            a = {
                "i": i * 100,
                "n": 0,
            }
            l.append(a)
        s = json.dumps(l)

        if len(s) > 10000:
            INFO_MSG("too large data streamString cards ", len(s))
            self.streamStringToClient(s, "ownedcards")
        else:
            self._c_syncOwnedCardListToClient(s)


    def streamCardDataToClient(self):
        if not self.client:
            return
        #TODO 热更后清理C++的缓存
        INFO_MSG("streamCardDataToClient avatar")
        self.streamFileToClient(KBEngine.getResFullPath("server_common/D_CARD.json"), "d_card")

    #c STRING
    def _c_syncOwnedCardListToClient(self, s):
        if self.client: self.client._c_syncOwnedCardListToClient(s)

    def onStreamComplete(self, id, success):
        if success != True:
            ERROR_MSG("stream error")
            self.tryDestroy()
            return
        INFO_MSG("sync all cards complete")

    #c LIST_SIMPLE_CARD_DATA
    def c_testSendCardData(self, cardDataList):
        if self.client: self.client.c_testSendCardData(cardDataList)


    def __________________________________efunc(self):
        pass


    #e
    def e_reqPublicSpaces(self):
        if not self.checkTime("e_reqPublicSpaces",0.5):
            return
        # baseAppData["space_" + str(self.roomID)] = {"mail": self,
        #                                             "sceneName": self.sceneName,
        #                                             "spaceName": self.spaceName,
        #                                               "roomID":123
        #                                             "lan":"en",
        #                                             "password":""
        #                                             }
        # baseAppData["p_" + str(self.roomID)] = 0

        roomsJ={} #roomID:{}
        for n,j in baseAppData.items():
            if n[:6]=="space_":
                nroomID=int(n[7:])
                if nroomID not in roomsJ:
                    roomsJ[nroomID]={}
                tempj=roomsJ[nroomID]
                tempj["sceneName"]=j['sceneName']
                tempj["spaceName"]=j['spaceName']
                tempj["roomID"]=j['roomID']
                tempj["lan"]=j['lan']
                if len(tempj["password"]):
                    tempj["hasPassword"]=True
                else:
                    tempj["hasPassword"]=False

            elif n[:2]=="p_":
                nroomID=int(n[3:])
                if nroomID not in roomsJ:
                    roomsJ[nroomID]={}
                roomsJ[nroomID]["p"]=j


        result=list(roomsJ.values())
        self.c_onReqPublicSpaces(result)


    #c LIST_SPACE_REQ_JSON
    def c_onReqPublicSpaces(self,l):
        if self.client:self.client.c_onReqPublicSpaces(l)


    #e ID STRING
    def e_reqJoinPublicSpace(self,roomID,password):
        if not self.checkTime("e_reqJoinPublicSpace",0.2):
            return
        n="space_"+str(roomID)
        if n not in baseAppData:
            return

        spaceBA=baseAppData[n]["mail"]

        #check password
        truePass=baseAppData[n]["password"]
        if len(truePass):
            if truePass!=password:
                self.c_showLabel("joinSpacePasswordWrong")
                return

        self.tryToLoginToSpace(spaceBA)


    def __________________________________endeFucnc(self):
        pass



    def _______________________________________________spacefunc(self):
        pass


    #e
    def e_loginToHome(self):
        self.tryToLoginToSpace(self.account.myHome)

    # def tryToLeaveSpace(self):
    #     #强制退出房间,会进入到IdleScene,同时cell become null
    #     if not self.checkLock("tryTeleport"):
    #         return
    #     self.startCoroutine(self.y_tryToLeaveSpace(),self.onTryToLoginToSpaceOverTime,10,True,True)
    #
    # def y_tryToLeaveSpace(self):
    #     if self.cell:
    #         self.cell.tryDestroy()
    #         yield "onLoseCell"
    #
    #     DEBUG_MSG("try to leave space and enter idle space")
    #     self.c_switchScene(SCENENAME_IdleScene,True,True)
    #     success,pos, rot = yield "e_onSwitchSceneOver"
    #     self.cellData["position"] = pos
    #     self.cellData["direction"] = rot
    #     self.createCellEntity(self.account.idleScene)
    #     self.createCellTime = time.time()
    #     self.sceneName=SCENENAME_IdleScene
    #     yield "wait"
    #     self.unlock("tryTeleport")

    #e
    def e_leaveSpace(self):
        self.tryToLoginToSpace(self.account.idleScene)


    #p CALL
    def tryToLoginToSpace(self, spaceBA):
        #尝试进入某个房间,如果已经在房间里可以强制调用,一旦出错客户端会进入IdleScene
        """
        1 request space for login in
        2 try to destroy cell
        3 make client switch scene
        4 create cell
        """
        if not self.checkLock("tryTeleport"):  #add lock
            WARNING_MSG("tryToLoginToSpace multi times")
            return
        self.busy.setBusy(2)
        #给客户端50秒的时间,如果50秒都没能完成,就强制破坏
        self.startCoroutine(self.y_tryToLoginToSpace(spaceBA), self.onTryToLoginToSpaceOverTime, 50, True, True)


    def y_tryToLoginToSpace(self, spaceBA):
        DEBUG_MSG("start logintospace cor")
        self.sceneName = ""

        spaceBA.avatarLogin(self)
        err, spaceCE, sceneName,spaceType = yield "onLoginToSpace"
        if err != SUCCESS:
            ERROR_MSG("join space failed")
            self.c_showBannerNOCB("", "join failed")
            self.unlock("tryTeleport")
            if sceneName!=SCENENAME_IdleScene: #加入房间失败,但不是加入idle房间失败,就进入idle房间
                self.setInterval(0.2,0,self.onTimerJoinIdleSpace)
            else:
                self.tryDestroy()
            return

        if self.cell:
            self.cell.tryDestroy()
            yield "onLoseCell"

        #可以加入
        if self.client:
            self.c_switchScene(sceneName, spaceType,False,True)
            success,pos, rot = yield "e_onSwitchSceneOver"
            if success==SUCCESS:
                #success login to space
                self.cellData["position"] = pos
                self.cellData["direction"] = rot
                self.createCellEntity(spaceCE)
                self.createCellTime = time.time()
                self.sceneName = sceneName
                self.unlock("tryTeleport")
                INFO_MSG("avatarBA %d logintoSpace %s success" % (self.id, sceneName))
            else:
                #客户端找不到场景,或者客户端正在加载某个场景中,就强制破坏
                ERROR_MSG("client load scene "+sceneName+" error ="+success)
                self.unlock("tryTeleport")
                self.tryDestroy()

        else:  #有可能发生没有client的情况
            WARNING_MSG("c_switchScene no client")
            self.unlock("tryTeleport")
            self.tryDestroy()

    def onTimerJoinIdleSpace(self,tid):
        self.tryToLoginToSpace(self.account.idleScene)

    def onTryToLoginToSpaceOverTime(self, current):
        ERROR_MSG("onTryToLoginToSpaceOverTime", current)
        self.unlock("tryTeleport")
        self.tryDestroy()

    def onLoseCell(self):
        self.sceneName = ""
        if self.isDestroying:
            self._destroy2()
        elif self.hasLock("tryTeleport"):  #正在传送中
            self.onCallBack("onLoseCell")
        else:
            #cell自己破坏了,就进入idle
            self.tryToLoginToSpace(self.account.idleScene)

    #p ERROR CALL STRING UINT8
    def onLoginToSpace(self, err, spaceCE, sceneName,spaceType):
        DEBUG_MSG("callback onLoginToSpace")
        self.onCallBack("onLoginToSpace", err, spaceCE, sceneName,spaceType)

    #c STRING UINT8 BOOL BOOL
    def c_switchScene(self, sceneName,spaceType, isFocus,shouldCB):
        #sceneName如果是city/city就说明是bundle内的,如果是HelloScene没有/就说明是本包自带的
        #isFocus如果是true就是在一帧内切换场景,而不进行fade,只有场景在主包里才能做到
        if self.client: self.client.c_switchScene(sceneName,spaceType, isFocus,shouldCB)


    #e UINT8 VECTOR3 VECTOR3
    def e_onSwitchSceneOver(self,success, pos, dir):
        if self.hasCoroutine("y_tryToLoginToSpace"):
            self.onCallBack("e_onSwitchSceneOver", success,pos, dir)


    # def focusSwitchToIdleScene(self):
    #     self.sceneName=SCENENAME_IdleScene
    #     if self.cell:
    #         self.cell.tryDestroy()
    #     else:
    #         self.createCellEntity(self.account.idleScene)
    #     self.c_switchScene(SCENENAME_IdleScene,True,False)

    def _______________________________________________scenefuncend(self):
        pass

    def _____________________________________________________clientFunc(self):
        pass

    #c STRING
    def c_showLabel(self, STRING):
        if self.client: self.client.c_showLabel(STRING)

    #c STRING STRING
    def c_showBannerNOCB(self, title, text):
        if self.client: self.client.c_showBannerNOCB(title, text)

    def showBannerOKBaseCB(self, title, text, cb):
        self.c_showBannerBaseCB(title, text, ["OK"], cb)

    #c STRING STRING LIST_STRING STRING
    def c_showBannerBaseCB(self, title, text, options, cb):
        if self.client: self.client.c_showBannerBaseCB(title, text, options, cb)

    #e STRING UINT8
    def e_onBannerBaseCB(self, cb, cnt):
        func = getattr(self, cb, None)
        if func:
            func(cnt)
        else:
            ERROR_MSG("banner base cb not exist ", cb)

    #c UNICODE
    def c_DEBUG_MSG(self, s):
        if self.client: self.client.c_DEBUG_MSG(s)

    #c UNICODE
    def c_WARNING_MSG(self, s):
        if self.client: self.client.c_WARNING_MSG(s)

    #c UNICODE
    def c_ERROR_MSG(self, s):
        if self.client: self.client.c_ERROR_MSG(s)


    #e UINT8 UNICODE
    def e_clientSendLog(self,t,logdata):
        if t==2:
            ERROR_MSG("CLIENT_ERROR:"+logdata)


    #e UNICODE
    def e_reportData(self,uni):
        j=json.loads(uni)
        email=j["email"]
        type=j["type"]
        content=j["content"]

        if type=="bug":
            pass
        elif type=="advice":
            pass


    def _____________________________________________________clientFuncend(self):
        pass

    def _____________________________________________________friend(self):
        pass

    def followFriend(self, dbid):
        pass

    def c_updateFriendState(self):
        pass

    def sendMessageToFriend(self, dbid):
        pass

    def ________________________________________friendEnd(self):
        pass

    def __________________________________________card(self):
        pass

    #c STRING
    def c_downloadDebugCardData(self, s):
        """

{
        "id": 3000,
        "key": "demonlord",
        "name_en": "Demon Lord",
        "name_zh": "恶魔领主",
        "name_zh_tr": "",
        "name_ja": "",
        "package": "demonlord",
        "radius2x": 0.0,
        "category": "Minion",
        "attack": 1,
        "defense": 1,
        "health": 1,
        "attr": 0,
        "camp": 0,
        "level": 0,
        "race": 0,
        "alignment": 0,
        "effect_en": "",
        "effect_zh": "",
        "effect_zh_tr": "",
        "effect_ja": "",
        "disable": 0
    }

        """
        pass

    #e
    def e_open1Pack(self):
        #抽一包卡,最简单的方式,从所有卡里面随机分配
        #5张
        if isDebugVer():
            return


    def _____________________________endCard(self):
        pass


    #e STRING STRING
    def e_becomeRegular(self,accName,password):
        self.accountFunc.becomeRegular(accName,password)

    #c
    def c_onBecomeRegularSuccess(self):
        if self.client:self.client.c_onBecomeRegularSuccess()

    #e STRING
    def changePass(self,password):
        self.accountFunc.changePass(password)

    #c
    def c_changePassSuccess(self):
        if self.client:self.client.c_changePassSuccess()


    #e
    def e_quitGame(self):
        self.tryDestroy()


    def onCellCrash(self):
        ERROR_MSG("avatar id=%d cell crash"%self.id)
        self.delayDestroy()

    #破坏自身,然后account延迟破坏
    def tryDestroy(self):
        if self.isDestroyed or self.isDestroying:
            return
        self.isDestroying = True

        self.closeAll()

        if self.cell:
            self.cell.tryDestroy()
        else:
            self._destroy2()

    def _destroy2(self):
        if self.account:
            self.account.avatarBA = None
            self.account.waitLongtimeDestroy()
            self.account = None
        self.destroy()



    def delayDestroy(self):
        self.setInterval(0.1, 0, self.onDelayDestroy)

    def onDelayDestroy(self, tid):
        self.tryDestroy()


    def onClientDeath(self):
        if self.hasAnyCoroutine() or self.hasAnyLock():
            WARNING_MSG("avatar death has coroutine")
            self.tryDestroy()
            return

        if self.cell:
            self.cell.onClientDeathCell()

        if self.account:
            self.account.onAvatarClientDeath()  #延迟一段时间后破坏
        else:
            ERROR_MSG("cdcdscsdcsdc")
            self.tryDestroy()


    def onDestroy(self):
        pass
