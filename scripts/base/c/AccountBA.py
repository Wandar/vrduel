# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2018 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2018-04-05 15:44
from __future__ import annotations

import sys
import zlib

from KBEngine import *

from ServerDeploy import s_ServerDeploy
from c.ProxyBA import ProxyBA
from util import *
from annos import *



"""
优化:
    玩家推出不立刻破坏account


功能:
    管理avatar和space的生命
    内购处理
    一些需要长期储存的数据保存
    保存该玩家的空间实例,比如家,野外冒险地图
    
    
    
owncardlist结构

normalcards=
[
{
    "i":200, #卡片id,
    "n",4 #数量
},
{

}
],
这个功能之后再实现
sepcialcards=
[
{
"i":200,
"id":187263876478364, #全局唯一id
"exp":300,
"lv":3
"rare":1
"skin":
"acce":[]
}
]


decklist结构
[
{
"id":
"a"
"b"
"c"
}

]

"""

ACCOUNT_MAX_ENERGY=40


class AccountBA(ProxyBA):
    myHome = None  #type:SpaceBA
    idleScene=None #type:SpaceBA
    tutorialRoom = None  #type:SpaceBA
    avatarBA = None  #type:AvatarBA

    _clientDeathTime = 0

    ########################################STORED
    #c BASEC BOOL STORED
    c_registered=False
    #c BASE STRING STORED
    accountName=""
    #c BASE INT8 STORED
    clientType=0
    #c BASEC STRING STORED
    uniIDstr=""
    #c BASE UINT32 STORED
    _energy=0
    #c BASE BOOL STORED
    isTutorialCompleted = False
    #c BASEC UNICODE STORED
    nickName = ""
    #c BASEC STRING STORED
    homeSceneName = ""
    #c BASEC BOOL STORED
    c_blockDownload=False


    #c BASE STRING STORED
    languagecode = ""
    #c BASE STRING STORED
    country = ""
    #c BASE STRING STORED
    l=""
    #c BASE STRING STORED
    lastLoginDate = ""


    #c BASE UINT64 STORED
    coin=0
    #c BASE UINT64 STORED
    bcrystal=0
    #c BASE UINT64 STORED
    wcrystal=0

    #c BASE BLOB STORED
    storedLongData = ""  #{"owncardlist":[],"decklist":[]} 最大到16M
    #c BASE BOOL STORED
    storedDataCompress=False
    #c BASE UINT32 STORED
    storedDataLen=0
    owncardlist = {}  #[{"i":200,"n":400},{}]
    decklist = []
    homeJson={} #display card in home scene



    ###############################################

    longtimedeathTid = 0
    mainTimerTid = 0
    def onLoad(self):
        DEBUG_MSG("create Account")

        ASSERT_MSG(self.databaseID, "accountBA no databaseID")

        self.decompressData()
        if not self.c_registered:
            if not checkIsGuestAccount(self.__ACCOUNT_NAME__):
                self.c_registered=True


        if not self.homeSceneName:
            self.homeSceneName = "HomeScene"

        if not self.uniIDstr:
            self.uniIDstr=number64toStr(genUUID64())
            self.writeToDB()

        self.myHome = createEntityLocally("Space", {
            "sceneName": self.homeSceneName,
            "spaceType": SPACE_TYPE.home,
            "owner": self,
        })
        self.idleScene = createEntityLocally("Space", {
            "sceneName": SCENENAME_IdleScene,
            "spaceType": SPACE_TYPE.idle,
            "owner": self,
        })


        #TODO
        # if self.isTutorialCompleted:
        # self.tutorialRoom=createEntityLocally("Space", {
        #     "sceneName":"TutorialScene",
        #     "owner":self,
        # })

        getGameManager().onPlayerEnter(self.databaseID,self.uniIDstr,self)


    def start(self):
        self.genDeckData()


    def decompressData(self):
        if not self.storedLongData:
            return
        if self.storedDataCompress:
            s=zlib.decompress(self.storedLongData)
        else:
            s=self.storedLongData
        j=json.loads(bytes.decode(s),encoding='utf-8')


    def mainTimer(self, tid):
        pass

    def genDeckData(self):
        a = {
            "name": "commonDeck",
            "data": ""
        }
        j = {
            "a": [],
            "b": [],
            "c": [],
            "side": []
        }
        for i in range(40):
            j["a"].append(200)
        a["data"] = json.dumps(j)



    def checkLoginDateAndSendGifts(self):
        today = time.strftime("%Y.%m.%d", time.localtime())
        if self.lastLoginDate != today:
            self.lastLoginDate = today
            #TODO
            #发放奖励
            self._energy=ACCOUNT_MAX_ENERGY


    def useEnergy(self,cnt):
        self._energy=limitCal(self._energy,-cnt,0,ACCOUNT_MAX_ENERGY)
        if self.avatarBA:
            self.avatarBA._c_energy=self._energy

    def ______________________________________________________loginqueue(self):
        pass

    """
    login queue:
    ->onClientEnabled
    ->c_onLoginSuccess
    ->e_onLoginSuccessCB
    ->_onClientEnabledAndCreateAvatar
    if already has avatar(断线重连): 
    ->c_switchSceneAccount(client switch scene)
    ->e_onAccountSwitchSceneOver(give to avatar)
    ->giveClientTo(avatar)
    else
    ->create avatar
    ->giveClientTo(avatar)
    ->avatar.onClientEnabled
    ->avatar.onClientLoginClickOK
    ->avatar.tryToLoginToSpace
    ->avatar.c_switchScene(client switch scene)
    ->avatar.e_onSwitchSceneOver
    ->avatar create cell entity
    """

    def onLogOnAttempt(self, ip, port, password):
        return LOG_ON_ACCEPT


    #first place while login
    def onClientEnabled(self):
        self.checkLoginDateAndSendGifts()

        #cancel destroy timer
        if self.longtimedeathTid:
            self.delInterval(self.longtimedeathTid)
            self.longtimedeathTid = 0

        if self.isDestroying:
            ERROR_MSG("account login destroying")
            self.destroy()
            return

        if self.avatarBA and self.avatarBA.client:
            self.avatarBA.disconnect()

        self._clientDeathTime = 0

        if self.getClientType() !=CLIENT_TYPE.web:
            self.clientType=self.getClientType()
            self.c_onLoginSuccess(s_ServerDeploy().getUpdatehz())

    def _onClientEnabledAndCreateAvatar(self):
        shouldReCreateAvatar = False
        if not REMAIN_AVATAR:
            shouldReCreateAvatar = True
        elif self.avatarBA:
            INFO_MSG("login has avatarBA")

            if not self.avatarBA.cell:
                WARNING_MSG("login to account avatar not has cell")
                shouldReCreateAvatar = True
            if self.avatarBA.hasAnyLock() or self.avatarBA.hasAnyCoroutine():
                ERROR_MSG("avatar maybe has error on it")
                shouldReCreateAvatar = True
            elif self.avatarBA.sceneName and self.avatarBA.cell:  #already has avatar
                self.c_switchSceneAccount(self.avatarBA.sceneName)  #e_onAccountSwitchSceneOver
                shouldReCreateAvatar = False
            else:
                shouldReCreateAvatar = True
        else:
            shouldReCreateAvatar = True

        if shouldReCreateAvatar:
            if self.avatarBA:
                self.avatarBA.account = None
                self.avatarBA.tryDestroy()
            self.avatarBA = createEntityLocally("Avatar", {})
            self.avatarBA.initAvatar(self)
            self.giveClientTo(self.avatarBA)

    #c UINT8
    def c_onLoginSuccess(self, updatehz):
        if self.client: self.client.c_onLoginSuccess(updatehz)

    #e STRING STRING STRING STRING
    def e_onLoginSuccessCB(self,cardver,lancode,country,l):
        self.languagecode = sqlFilter(lancode)
        self.country =sqlFilter(country)
        self.l=sqlFilter(l)
        self.accountName=self.__ACCOUNT_NAME__

        if cardver== D_CARD[0]["name_en"]:
            self._onClientEnabledAndCreateAvatar()
        else:
            self.c_showNotify("downloadingdata")
            self.streamCardDataToClient()

    def streamCardDataToClient(self):
        if not self.client:
            ERROR_MSG("streamCardDataToClient no client")
            self.tryDestroy()
            return
        self.streamFileToClient(KBEngine.getResFullPath("server_common/D_CARD.json"), "d_card")

    def onStreamComplete(self, id, success):
        if success != True:
            ERROR_MSG('stream error')
            self.tryDestroy()
            return
        INFO_MSG("stream ", id, success)
        self._onClientEnabledAndCreateAvatar()

    def onGiveClientToFailure(self):
        WARNING_MSG("onGiveClientToFailure")
        self.tryDestroy()


    #c STRING
    def c_switchSceneAccount(self, sceneName):  #只有断线重连才会用到
        if self.client: self.client.c_switchSceneAccount(sceneName)

    #e UINT8
    def e_onAccountSwitchSceneOver(self,success):
        if self.avatarBA and success==SUCCESS:
            #如果已经有avatarBA,就说明要重连,切换场景到该scene
            if self.avatarBA.client:
                ERROR_MSG("account give avatar has client")
                self.tryDestroy()
                return
            self.giveClientTo(self.avatarBA)
        else:
            ERROR_MSG("auisycbuyasc")
            self.tryDestroy()

    def ______________________________________loginqueueend(self):
        pass




    def _____________________________________________________clientFunc(self):
        pass

    #c UNICODE
    def c_showNotify(self, s):
        if self.client: self.client.c_showNotify(s)

    #c UNICODE
    def c_DEBUG_MSG(self, s):
        if self.client: self.client.c_DEBUG_MSG(s)

    #c UNICODE
    def c_WARNING_MSG(self, s):
        if self.client: self.client.c_WARNING_MSG(s)

    #c UNICODE
    def c_ERROR_MSG(self, s):
        if self.client: self.client.c_ERROR_MSG(s)


    #e UNICODE
    def e_submitCardSuggestion(self, titleandcontent: str):
        if not self.checkTime("e_submitCardSuggestion", 2):
            return
        if len(titleandcontent) > 20000:
            return
        j = json.loads(titleandcontent)
        type = j["type"]
        title = j["title"]
        content = j["content"]
        contact = j["contact"]
        accountID = self.databaseID

        if type == "cardsuggestion":
            sqlt = 'insert into cardsuggestion(subtitle,content) values ("%s","%s");' % (title, content)
        else:
            sqlt = 'insert into suggestion(subtitle,content) values ("%s","%s");' % (title, content)
        executeRawDatabaseCommand(sqlt, self.onSubmitMessage)

    def onSubmitMessage(self, result, rows, insertid, error):
        INFO_MSG("onSubmitMessage ", result, rows, insertid, error)



    def ______________________________________________________clientfuncend(self):pass


    def _______________________________________________________browserfunc(self):pass



    def _______________________________________________________browserfuncend(self):pass
    
    
    
    def _______________________________________________accountfunc(self):
        pass






    def ________________________________________________endaccountfunc(self):
        pass



    def onWriteToDB(self, cellData):
        j = {"owncardlist": [], "decklist": []}
        s=json.dumps(j).encode(encoding='utf-8')

        lens=len(s)
        self.storedDataLen=lens
        self.storedDataCompress=True
        if lens>1024*1024*2: #dont compress save cpu
            self.storedDataCompress=False
            ERROR_MSG("storeddata too big l=",lens)

        if lens>1024*1024*15.5: #too big,should compress
            self.storedDataCompress=True

        if self.storedDataCompress:
            timePre()
            self.storedLongData = zlib.compress(s)
            timeLog("compress dataLen %d"%lens)
        else:
            self.storedLongData=s



    #when player logout
    def onAvatarClientDeath(self):
        self._clientDeathTime = time.time()
        self.waitLongtimeDestroy()


    #一般不太可能进来,一般会进onAvatarClientDeath
    def onClientDeath(self):
        WARNING_MSG("Account onClientDeath")
        self.waitLongtimeDestroy()



    #wait 20min then destroy
    def waitLongtimeDestroy(self):
        if self.longtimedeathTid:
            self.delInterval(self.longtimedeathTid)

        waittime=60 * 20
        if isDebugVer():
            waittime=1
        self.longtimedeathTid = self.setInterval(waittime, 0, self.onTimerLongTimeDestroy)

    def onTimerLongTimeDestroy(self, tid):
        self.longtimedeathTid = 0
        self.tryDestroy()

    #destroy everything
    def tryDestroy(self):
        if self.isDestroying or self.isDestroyed:
            return

        getGameManager().onPlayerDestroy(self.databaseID,self.uniIDstr,self.id)
        self.isDestroying = True
        if self.avatarBA:
            #因为每次有改变都会立刻同步到account,所以不必等待数据同步
            self.avatarBA.tryDestroy()
            self.avatarBA = None
        if self.myHome:
            self.myHome.tryDestroy()
            self.myHome = None
        if self.tutorialRoom:
            self.tutorialRoom.tryDestroy()
            self.tutorialRoom = None
        if self.idleScene:
            self.idleScene.tryDestroy()
            self.idleScene=None

        self.destroy()

    def onDestroy(self):
        #如果是服务器自动删除可能进入这里
        getGameManager().onPlayerDestroy(self.databaseID,self.uniIDstr,self.id)

