# -*- coding: utf-8 -*-
from __future__ import annotations

import sys

from KBEngine import *

from ServerDeploy import s_ServerDeploy
from c.ComponentBA import ComponentBA
from util import *
from annos import *


#功能:
#总房间管理器,总玩家管理器

#得到总玩家人数,按照玩家人数余量创建space
#读取spaces的信息,在客户端显示
#玩家登陆space

# MIN_SPACE_NUM=5

#超过60秒就不要再加人了


#space 家园space,公共作战,匹配作战

# class SpaceData:
#     roomID = ""
#     # state = SPACE_STATE.initing
#     load = 0
#     mail = None  #type:SpaceBA
#     spaceType = 0
#     sceneName = 0  #bundle name
#     playerCount = 0
#     usedCnt = 0

class DuelPlaceData:
    roomID=0
    order=0
    stressload=0
    playEndTime=0
    isUsing=False


"""
玩家可以创建public space,(当然限制数量)


"""
CREATE_ROOM_INTERVAL = 5


class SpaceManagerBA(ComponentBA):
    isFirstRoomInited = False
    debugSpace = None  #type:DebugSpace
    debugSpaceRoomKey = 0

    crashedCellNum = 0

    _curJoinSpaceIDs = None

    _spaces = None  #type:Dict[str,SpaceData]
    _createRoomCnt = 0

    queues = None  #type:Dict[int,List[Union[AccountBA,TeamData]]]

    cellNum = 0

    testTid = 0


    spaceIDPool=None

    def onLoad(self):
        globalData["SpaceManager"] = self
        self._spaces = {}


        self._initSpaceIDPool()
        # self.setInterval(0.1,0.1,self.onTimerJoinQueue)

        #create Debug
        # if CREATE_DEBUG_ROOM:
        #     self.createDebugSpace()

        #create Rooms
        # if SHOULD_START_GAME:
        #     self.setInterval(0.1, 3, self.onTimerRecalCellNumAndCreateRoom)

        #房间太少就创建,太多就破坏
        self.onTimerCheckDate(0)
        # self.setInterval(1, 5, self.onTimerSpaceMgr)

        #一次性
        self.setInterval(60,0,self.onTimerSendInitStatus)


    def start(self):
        pass


    def onTimerSendInitStatus(self, tid):
        title = s_ServerDeploy().getServerName() + " initStatus "
        num=getPublicSpaceNum()
        a="inited public space = %d"%num
        MAIL_MSG(title, a)



    def _________________________publicSpaceAndPrivateSpace(self):
        pass

    def genRoomID(self):
        iid=0
        for i in range(1, MAX_PUBLIC_SPACE_NUM):
            if i in self.spaceIDPool:
                del self.spaceIDPool[i]
                iid=i

        if iid==0:
            ERROR_MSG("not has roomID")
            return
        return iid

    #p ID
    def onSpaceDestroy(self, roomID):
        if roomID:
            self.spaceIDPool[roomID]=True
        #TODO 删除所有DuelPlace


    def _initSpaceIDPool(self):
        self.spaceIDPool={}
        for i in range(1, MAX_PUBLIC_SPACE_NUM):
            self.spaceIDPool[i]=True

    def onTimerSpaceMgr(self, tid):
        self.onTimerCheckRooms(tid)
        self.onTimerCheckDate(tid)


    def onTimerCheckRooms(self, tid):
        cnt=getPublicSpaceNum()
        if cnt<3:
            shouldAdd=3-cnt
            for i in range(shouldAdd):
                self.createSpace(SPACE_TYPE.mpublic,"simpleScene","Public Room","","en")
        elif cnt>20:
            #找几个玩家数量为0的破坏掉
            delNum=cnt-20
            dels=[]
            for nname,num in baseAppData.items():
                if nname[:2]=="p_":
                    roomID=int(nname[3:])
                    if num==0:
                        createTime=baseAppData["space_"+str(roomID)]["createTime"]
                        if time.time()-createTime>60*5: #少于5分钟的不破坏
                            dels.append(roomID)
            if len(dels):
                random.shuffle(dels)
                for i in range(len(dels)-1,-1,-1):
                    roomID=dels[i]
                    spaceBA=baseAppData["space_"+str(roomID)]["mail"]
                    spaceBA.tryDestroy()
                    delNum-=1
                    if delNum==0:
                        break


    lastCheckDay=None
    todayMatchMapName=""
    def onTimerCheckDate(self,tid):
        today = time.strftime("%Y.%m.%d", time.localtime())
        if self.lastCheckDay!= today:
            self.lastCheckDay = today
            #TODO 随机选一种房间为匹配专用



    #p UINT8 STRING UNICODE STRING STRING
    def playerReqCreateSpace(self,spaceType, sceneName,spaceName,password,lan):
        if len(self.spaceIDPool)==0:
            ERROR_MSG("reqCreate space not has space")
            return
        self.createSpace(spaceType, sceneName,spaceName,password,lan)


    def createSpace(self, spaceType, sceneName,spaceName,password,lan):
        if "isShutdowning" in globalData and globalData["isShutdowning"]:
            ERROR_MSG("want to createSpace while shutdowning")
            return

        roomID=0
        if spaceType == SPACE_TYPE.mpublic:
            roomID=self.genRoomID()
        INFO_MSG("create Room id=%d ,type = %d" % (roomID, spaceType))

        createType = "Space"

        # a = SpaceData()
        # a.roomKey = roomKey
        # a.state = SPACE_STATE.creating
        # a.spaceType = spaceType
        # a.sceneName = sceneName
        # self._spaces[roomKey] = a

        createEntityAnywhere(createType,
                             {
                                 "sceneName": sceneName,
                                 "spaceName":spaceName,
                                 "spaceType": spaceType,
                                 "password":password,
                                 "lan":lan,
                                 "owner": None,
                             }, self.onCreateSpace)

    def onCreateSpace(self, mail):
        pass

    # def destroyMySpace(self, roomKey):
    #     # self.roomStopJoinByRoomID(roomID)
    #     for iid, spaceData in tuple(self._spaces.items()):
    #         if 0: spaceData = spaceData  #type:SpaceData
    #         if iid == roomKey:
    #             if spaceData.state == SPACE_STATE.creating:
    #                 ERROR_MSG("destroy creating space")
    #                 return
    #             else:
    #                 spaceData.mail.tryDestroy()
    #                 del self._spaces[iid]


    def _________________________publicSpaceAndPrivateSpaceend(self):
        pass






    def createDebugSpace(self):
        roomKey = number64toStr(genUUID64(),True)
        sceneName="DebugSpace"
        createEntityAnywhere("DebugSpace", {
            "sceneName":sceneName,
            "spaceType": SPACE_TYPE.debug,
            "owner":None,
            "roomKey": roomKey,
        }, Functor(self._onCreateDebugSpace, roomKey))

    def _onCreateDebugSpace(self, roomKey, space):
        self.debugSpaceRoomKey = roomKey
        self.debugSpace = space



    #p STRING
    def onSpaceCellCrash(self, roomKey):
        ERROR_MSG("space cell crash room", roomKey)
        self.crashedCellNum += 1
        del self._spaces[roomKey]

    #p
    def resetDebugSpace(self):
        INFO_MSG("reset DebugSpace")
        if self.debugSpace:
            self.debugSpace.tryDestroy()
        if self.debugSpace2:
            self.debugSpace2.tryDestroy()
        self.createDebugSpace()

    def resetAll(self):
        for id, spaceData in self._spaces.items():
            spaceData.mail.tryDestroy()
        self._spaces.clear()
        self.cellNum = 0

    debugSpaceNameID = 2

    def _onCreateDebugSpace2(self, roomID, space):
        self.debugSpace2RoomID = roomID
        self.debugSpace2 = space

    #p CALL
    def reqJoinDebugSpace(self, accountBA):
        if self.debugSpace:
            accountBA.pleaseLoginToSpace(SUCCESS, self.debugSpace, self.debugSpaceNameID)

    #有时无效,改timer
    # def newCellAdded(self):
    #     self.onTimerRecalCellNumAndCreateRoom()

    #p ID UINT8
    def spaceSetState(self, roomID, state):
        spaceData = self._spaces[roomID]
        spaceData.state = state
        spaceType = spaceData.spaceType
        if state == SPACE_STATE.idle:
            INFO_MSG("space%d initOK", roomID)
            if not self.isFirstRoomInited:
                self.isFirstRoomInited = True
                self._sendFirstRoomInited()
            self.roomStopJoinByRoomID(roomID)
            #使用超过100次的房间删除掉
            if spaceData.usedCnt > 100:
                INFO_MSG("space over cnt and destroy")
                self.destroyMySpace(roomID)
                self.createSpace(0, spaceType)
        elif state == SPACE_STATE.initing:
            self.roomStopJoinByRoomID(roomID)
            pass

    def _sendFirstRoomInited(self):
        title = s_ServerDeploy().getServerName() + " firstRoomInited "
        MAIL_MSG(title, title)



    #p ID
    def spaceReqReinit(self, roomID):
        spaceData = self._spaces[roomID]
        spaceData.state = SPACE_STATE.initing
        spaceData.mail.cell.onReqReinitSpace()

    def getBaseNum(self):
        num = 0
        for name, a in globalData.items():
            if name[:7] == "baseapp":
                num += 1
        return num

    def onTimerRecalCellNumAndCreateRoom(self, tid):
        createNum = NORMAL_SPACE_NUM_PER_CELL
        if not publish():
            createNum = DEBUG_NORMAL_SPACE_NUM_PER_CELL
        num = 0
        for name, a in globalData.items():
            if name[:7] == "cellapp":
                num += 1
        if num < self.cellNum:
            ERROR_MSG("cellapp descreased ???!!!", num)
        elif num > self.cellNum:
            for i in range(self.cellNum + 1, num + 1):  #从selfcellNum+1到num
                for n in range(createNum):
                    # if self.crashedCellNum==0:
                    #     createCellNum=i
                    # else:
                    #每次都不同的
                    createCellNum = 0
                    self.setInterval(20 * n + 1, 0, FunctorTid(self.createSpace, createCellNum, SPACE_TYPE.normal))
                for n in range(WAR_SPACE_NUM_PER_CELL):
                    createCellNum = 0
                    self.setInterval(20 * n + 1, 0, FunctorTid(self.createSpace, createCellNum, SPACE_TYPE.war))
        self.cellNum = num

    def testfuncSpaceManager(self):
        if not getattr(Entity, "setInterval", None):
            sys.exit(0)



    # def y_login(self,playerCall):
    #     self.cell.getPlayerNum()
    #     playerNum=yield "onGetPlayerNum"
    #     if playerNum>70:
    #         getSpaceManagerBA().spaceOnLogin(playerCall.id,FAIL)
    #     else:
    #         success

    def onTimerJoinQueue(self, tid):
        if not self.isFirstRoomInited:  #防止刚开服时拥挤
            return

        if globalData["isShutdowning"]:
            return

        maxDealNum = 100  #一次最大处理100个人要出来,防止卡死
        for playType, queue in self.queues.items():
            if len(queue) > 300:
                ERROR_MSG("queue playType=%d over player" % playType)
            for i in range(len(queue) - 1, -1, -1):
                maxDealNum -= 1
                if maxDealNum < 0:
                    return
                data = queue[i]
                if TeamData.isSameType(data):
                    if 0: data = data  #type:TeamData
                    roomID = self.chooseSpace(playType, len(data.playerList))
                    if not roomID:
                        break
                    else:
                        spaceData = self._spaces[roomID]
                        s = spaceData.mail
                        #先给队伍预留位置
                        s.cell.setTeamSlot(data.teamID, len(data.playerList), data.shouldFill)
                        data.broadcastPlayer("pleaseLoginToSpace", SUCCESS, s, spaceData.sceneNameID)
                        del queue[i]
                else:  #AccountBA
                    if 0: data = data  #type:AccountBA

                    roomID = self.chooseSpace(playType, 1)
                    if not roomID:
                        break
                    spaceData = self._spaces[roomID]
                    s = spaceData.mail  #type:SpaceBA
                    if spaceData.state == SPACE_STATE.idle:
                        TEMP_ERROR('enter IDLE space')
                    data.pleaseLoginToSpace(SUCCESS, s, spaceData.sceneNameID)
                    del queue[i]

    #房间不够了
    def limitedCreateSpace(self, spaceType):
        if not self.checkTime("limitedCreateSpace_%d" % spaceType, 5):
            return
        maxSpaceNum = self.cellNum * SPACENUM_PER_CELL_WARN_NUM
        if len(self._spaces) >= maxSpaceNum:
            ERROR_MSG("space num too many ", len(self._spaces))
        acc = self  #type:AccountManagerBA
        WARNING_MSG("cant found a room to join, maybe too less,current playNum ", len(acc._accounts))
        self.createSpace(0, spaceType)

    #p UINT8 ID
    def roomStopJoin(self, playType, roomID):
        if roomID == self._curJoinSpaceIDs[playType]:
            self._curJoinSpaceIDs[playType] = 0

    def roomStopJoinByRoomID(self, roomID):
        for playType, iid in self._curJoinSpaceIDs.items():
            if iid == roomID:
                self._curJoinSpaceIDs[playType] = 0

    def ___________________testTrans(self):
        pass

    #p CALL
    def testTransMap(self, avaBA: AvatarBA):
        avaBA.isTeleporting = True
        avaBA.destroyCellEntity()
        self.debugSpace2.reqTeleport(avaBA)

    def ___________________testTransEnd(self):
        pass

    """检查当前加入的服务器是否可加
            不可加的话选择新的服务器,startGame
    """

    def chooseSpace(self, playType, numToJoin):
        if playType in (PLAY_TYPE.player1, PLAY_TYPE.player2, PLAY_TYPE.player4):
            shouldSpaceType = SPACE_TYPE.normal
        elif playType == PLAY_TYPE.war:
            shouldSpaceType = SPACE_TYPE.war
        else:
            ERROR_MSG("sadgasuyd")

        roomID = self._curJoinSpaceIDs[playType]
        if roomID:
            spaceData = self._spaces[roomID]
            spaceData.joinCount += 1
            if spaceData.joinCount > self.maxJoinNumEver:
                self.maxJoinNumEver = spaceData.joinCount
            if spaceData.joinCount > 255:
                ERROR_MSG('one tick join too much')
                roomID = 0
            elif spaceData.state == SPACE_STATE.inGame:
                return roomID

        #满了或者超时了找下一个
        roomID = 0
        curLoad = 10000
        self._curJoinSpaceIDs[playType] = 0
        for id, spaceData in self._spaces.items():
            if 0: spaceData = spaceData  #type:SpaceData
            if spaceData.spaceType != shouldSpaceType:
                continue
            if spaceData.state == SPACE_STATE.idle:  #在游戏中的不要
                #find lowest load
                if spaceData.load < curLoad:
                    roomID = id
                    curLoad = spaceData.load

        if roomID:  #founded init space
            spaceData = self._spaces[roomID]  #type:SpaceData
            spaceData.state = SPACE_STATE.inGame
            spaceData.mail.cell.startGame(playType)
            spaceData.usedCnt += 1
            spaceData.joinCount = 1
            self._curJoinSpaceIDs[playType] = roomID
        else:
            self.limitedCreateSpace(shouldSpaceType)

        return roomID

    def checkThereNoSpaceAndCreate(self):
        if publish():
            spaceIdleNum = self.cellNum
        else:
            spaceIdleNum = self.cellNum
        for shouldSpaceType in (SPACE_TYPE.normal, SPACE_TYPE.war):
            idleNum = 0
            for id, spaceData in self._spaces.items():
                if 0: spaceData = spaceData  #type:SpaceData
                if spaceData.spaceType != shouldSpaceType:
                    continue
                #得到空闲和创建中的数量
                if spaceData.state == SPACE_STATE.creating or spaceData.state == SPACE_STATE.initing:
                    idleNum += 1
            shouldCreate = spaceIdleNum - idleNum
            if shouldCreate > 0:
                for i in range(shouldCreate):
                    self.createSpace(0, shouldSpaceType)

    #p ID FLOAT
    def refreshLoad(self, roomID, load):
        self._spaces[roomID].load = load

    #p UINT8 CALL
    def reqPlayNoTeam(self, playType, accBA: "AccountBA"):
        self.queues[playType].append(accBA)

    #p UINT8 UINT32
    def reqPlayTeam(self, playType, teamID):
        #找人不满的加入
        accManager = self  #type:AccountManagerBA
        teamData = accManager.getTeamData(teamID)
        self.queues[playType].append(teamData)

    #p CALL
    def onePlayerReqPlay2(self, accBA: "AccountBA"):
        pass

    sceneGenInited = False
    normalMapGen = None  # {id:{value:10}}
    warMapGen = None

    def initSceneGen(self):
        self.normalMapGen = {}
        self.warMapGen = {}
        self.sceneGenInited = True
        for nameID, sceneJ in SCENE_J.items():
            if 'active' in sceneJ and sceneJ['active'] == False:
                continue
            self.normalMapGen[nameID] = sceneJ['gameMode']['normal']
            self.warMapGen[nameID] = sceneJ['gameMode']['war']

    def _spaceTypeToSceneNameID(self, spaceType):
        if not self.sceneGenInited:
            self.initSceneGen()
        nameID = 0
        if spaceType == SPACE_TYPE.normal:
            nameID = int(randDictWithWeight(self.normalMapGen, 'value'))
        elif spaceType == SPACE_TYPE.war:
            nameID = int(randDictWithWeight(self.warMapGen, 'value'))
        else:
            ERROR_MSG("viduivbfv")

        if not publish() and DEBUG_TEST_SPACE_ID:
            nameID = DEBUG_TEST_SPACE_ID
        return nameID

    def getIdleNum(self):
        num = 0
        for roomID, spaceData in self._spaces.items():
            if spaceData.state == SPACE_STATE.idle:
                num += 1
        return num

    def logSpaceStats(self):
        INFO_MSG('cellnum=%d' % self.cellNum)
        INFO_MSG('join space IDs =%d,%d,%d,%d' % (
            self._curJoinSpaceIDs[PLAY_TYPE.player1], self._curJoinSpaceIDs[PLAY_TYPE.player2],
            self._curJoinSpaceIDs[PLAY_TYPE.player4], self._curJoinSpaceIDs[PLAY_TYPE.war]))
        INFO_MSG('current Account num=%d' % (len(self.accountManagerBA._accounts),))
        idleNum = 0
        initingNum = 0
        inGameNum = 0
        spaceTypes = {
            SPACE_TYPE.normal: 0,
            SPACE_TYPE.war: 0
        }
        minLoad = 99999999
        maxLoad = 0
        for roomID, spaceData in self._spaces.items():
            if spaceData.state == SPACE_STATE.idle:
                idleNum += 1
            elif spaceData.state == SPACE_STATE.initing:
                initingNum += 1
            elif spaceData.state == SPACE_STATE.inGame:
                inGameNum += 1
            if spaceData.load < minLoad:
                minLoad = spaceData.load
            if spaceData.load > maxLoad:
                maxLoad = spaceData.load
            spaceTypes[spaceData.spaceType] += 1
        INFO_MSG('space idlenum=%d,inGameNum=%d,initingNum=%d' % (idleNum, inGameNum, initingNum))
        INFO_MSG('space normal=%d,war=%d' % (spaceTypes[SPACE_TYPE.normal], spaceTypes[SPACE_TYPE.war]))
        INFO_MSG('maxLoad=%f,minLoad=%f' % (maxLoad, minLoad))
        INFO_MSG('maxJoinNumEver=%d' % self.maxJoinNumEver)

    #p CALL
    def gmReqSpaceManager(self, gmMail):
        idleNum = 0
        initingNum = 0
        inGameNum = 0
        spaceTypes = {
            SPACE_TYPE.normal: 0,
            SPACE_TYPE.war: 0
        }
        minLoad = 99999999
        maxLoad = 0
        for roomID, spaceData in self._spaces.items():
            if spaceData.state == SPACE_STATE.idle:
                idleNum += 1
            elif spaceData.state == SPACE_STATE.initing:
                initingNum += 1
            elif spaceData.state == SPACE_STATE.inGame:
                inGameNum += 1
            if spaceData.load < minLoad:
                minLoad = spaceData.load
            if spaceData.load > maxLoad:
                maxLoad = spaceData.load
            spaceTypes[spaceData.spaceType] += 1
        gmMail.onReqSpace(len(self.accountManagerBA._accounts), spaceTypes[SPACE_TYPE.normal],
                          spaceTypes[SPACE_TYPE.war], maxLoad, minLoad)

    def onDestroy(self):
        if self.debugSpace:
            self.debugSpace.tryDestroy()

        if self.debugSpace2:
            self.debugSpace2.tryDestroy()

        for roomID, spaceData in self._spaces.items():
            spaceData.mail.destroyBaseAndCell()
            spaceData.mail = None

        del globalData["SpaceManager"]
