# -*- coding: utf-8 -*-



from __future__ import annotations
from datetime import datetime
from KBEngine import *

from b.Game import Game
from cards.cardPack1 import dame
from util import *
from annos import *

"""
连接逻辑和UI以及动画的桥梁

主要功能:
        保存在spaceCE里面的决斗信息
        给Game使用,调用客户端播放各种动画
        resolveMove接受玩家的操作,之后交给Game做逻辑处理
        

mainTaskLoop进行UI以及动画的播放以及等待
resolveMove接受玩家的操作

"""
"""
bridge between game logic and client shows    
"""
class Duel:
    duelID=0
    duelPlaceData=None #type:DuelPlace
    spaceCE=None #type:SpaceCE
    Game=None #type:Game

    #uniID:CardData
    usedCards=None #type:Dict[int][CardData]

    isDestroyed=False

    def __init__(self,tspaceCE,tduelID,tduelPlace:DuelPlace,avatarList):
        # self.WAIT, self.FUNC = Wait, Func
        # self.SEQUENCE, self.PARALLEL = Sequence, Parallel
        # self.LERP_Pos, self.LERP_PosHpr, self.LERP_PosHprScale = LerpPosInterval, LerpPosHprInterval, LerpPosHprScaleInterval
        # self.genCard = genCard

        self.spaceCE=tspaceCE

        self.duelID=tduelID
        self.duelPlaceData=tduelPlace

        self.usedCards={} #保存这场决斗相关的所有卡片 uniID:CardData

        self.boardID=0
        self.camp, self.showEnemyHand = 1, True
        self.btnBeingDragged = self.arrow = self.crosshair = self.np_Fatigue = self.np_YourTurnBanner = self.btnBoard = self.btnTurnEnd = None
        self.playedCards = [] #当手牌中的卡牌被打出后录入此列表，在clearDrawnCards和打出手牌时处理。
        self.np_CardZoomIn = self.np_Notification = None
        # Game play info related
        self.posMulligans = None
        self.mulliganStatus = {1: [0, 0, 0], 2: [0, 0, 0, 0]}
        self.subject = self.discover = None
        self.target = []
        self.pos = self.choice = -1

        self.step = ""
        self.stage = DUEL_STAGE.notingame
        # self.stage defines how cards respond to clicking.
        # -2:尚未进入游戏，还在组建套牌，-1:起手调试中，0:游戏中的闲置状态，还未选取任何目标，1:抉择中，2:选择了subject，3:发现选择中
        self.btns2Remove = []

        # Animation related
        self.gamePlayQueue = []
        # self.seqHolder, self.seq2Play, self.seqReady = [], None, False

        # Online Pvp related
        # self.sock_Recv = self.sock_Send = None
        # self.waiting4Server, self.msg_Exit, self.timer = False, '', 60

        # threading.Thread(target=self.keepExecutingGamePlays, name="GameThread", daemon=True).start()

        self.Game = Game(self)


        ASSERT_MSG(len(avatarList)==2,"acbiubyasbcyuacbys")
        self.avatars={1:avatarList[0],2:avatarList[1]} #type:Dict[int,AvatarCE]
        self.avatars[1].c_camp=1
        self.avatars[2].c_camp=2

        self.testFunc()


    def startGame(self):

        """

        开始游戏流程
        Hand_DECk mulliganBoth

        :return:
        """


        deck1=self.avatars[1].c_currentDeck
        deck2=self.avatars[2].c_currentDeck


        RNGPools=None
        seed = datetime.now().microsecond

        # self.Game.initialize_Details(self.boardID, int(seed), RNGPools, HD.heroes[1], HD.heroes[2], deck1=deck1,deck2=deck2)
        self.Game.initialize_Details(self.boardID, int(seed), RNGPools, None, None, deck1=deck1,deck2=deck2)

        self.Game.Hand_Deck.mulliganBoth()

        self.Game.changePhase(PHASE.mainphase1)

        # side=self.getPlayerAvatar().c_ID
        # self.getPlayerAvatar().c_handCard=[dame(self.Game,side),dame(self.Game,side),dame(self.Game,side),dame(self.Game,side),dame(self.Game,side)]
        # self.getPlayerAvatar().syncHandCard()


    def testFunc(self):
        # self.playanimDraw1Card(1,dame(self.Game,1))
        # self.playanimDraw1Card(1,dame(self.Game,1))
        # self.playanimDraw1Card(1,dame(self.Game,1))
        DEBUG_MSG("!!!!!!!!!!!!!!!!!!!!!!!!!!!!Duel testfunc 4545454545")
        pass

    def update01s(self):
        if self.isDestroyed:
            return
        self.keepExecutingGamePlays()

    def destroyGame(self):
        self.isDestroyed=True
        self.usedCards.clear()
        self.avatars.clear()


    #得到玩家avatar
    def getPlayerAvatar(self):
        for ID,avatar in self.avatars.items():
            if not avatar.c_isNPC:
                return avatar


    def registerCard(self,cardData):
        if cardData.uniID!=0:
            ERROR_MSG("card register twice")
            return
        cardData.uniID=self.spaceCE.genCardUniID()
        self.usedCards[cardData.uniID]=cardData


    def syncDuel(self,ID):
        #同步所有数据,包括手牌
        # self.avatars[ID].playanimSyncHandCard(self.Game.Hand_Deck)
        #TODO
        pass



    #trigger为0为按下,为1为放开
    def resolveMoveMainPhase(self,main1Or2,side,cardUniID,step):
        game=self.Game
        if game.whosmove!=side:
            return

        stage=self.stage
        avatar=self.avatars[game.whosmove]
        card=None
        if cardUniID in self.usedCards:
            card=self.usedCards[cardUniID]

        if step=="toMainPhase2":
            return

        if stage==DUEL_STAGE.normal:
            if step=="toBattlePhase":
                if main1Or2==PHASE.mainphase2:
                    return
                game.changePhase(PHASE.battle)

            elif step=="turnEnd":
                game.endTurn()

            elif step=="triggerDown":
                #卡牌可以使用
                #如果是通招怪物,enable summon
                #如果是指向魔法,指向+
                avatar.c_grabCard=card
                self.stage=DUEL_STAGE.cardgrabbed
                DEBUG_MSG("stage triggerDown")



        elif stage==DUEL_STAGE.cardgrabbed:
            if step=="triggerUp":
                return
        elif stage==DUEL_STAGE.decision:
                return



    def resolveMoveBattlePhase(self,side,cardUniID,step):
        game=self.Game
        if game.whosmove!=side:
            return
        stage=self.stage

        if step=="toBattlePhase":
            return

        if stage==DUEL_STAGE.normal:
            if step=="toMainPhase2":
                game.changePhase(PHASE.mainphase2)

            elif step=="turnEnd":
                game.endTurn()

            elif step=="triggerDown":
                pass

        elif stage==DUEL_STAGE.cardgrabbed:
            if "summon" in step:
                vecs=step[6:]
                vec=None
                try:
                    vec=json.loads(vecs)
                except Exception:
                    ERROR_MSG("vec error",vecs)
                    pass
                if not vec:
                    return
                v=(vec["x"],vec["y"],vec["z"])
        elif stage==DUEL_STAGE.decision:
                return


    def resolveMove(self,side,cardUniID,step):
        game=self.Game
        INFO_MSG("resolveMove ",cardUniID,step)
        if game.phase==PHASE.mainphase1 or game.phase==PHASE.mainphase2:
            self.resolveMoveMainPhase(game.phase,side,cardUniID,step)
        elif game.phase==PHASE.battle:
            self.resolveMoveBattlePhase(side,cardUniID,step)
        else:
            INFO_MSG("wrong phase resolveMove")
            return


    """
        step:
            toBattle
            turnEnd
            toMainPhase2
            triggerDown
            triggerUp
            summon{"x":,"y","z"}
            
            monsternormalSummon
            monsternormalSet
            
        stage:
            normal
            cardgrabbed
            decision

        基本操作:
            按下:手牌卡,场上卡
            弹起:地面,场上卡


        stage:
            右手没卡
            右手有卡,指向性

        能做的所有操作:
            召唤怪兽
            祭品召唤怪兽
            特殊召唤选择位置
            发动魔法
            发动指向魔法
            攻击
            切换表示
            
        只有召唤盖放和指向技能是可以直接用的,其他
            
        发生歧义时的选项:
            使用效果
            召唤怪兽
            盖放
    """

    def resolveMove2(self, entity, button, selectedSubject, info=None):
        print("Resolve move", entity, button, selectedSubject)
        print("Cur status", "subject", self.subject, "UI", self.UI, "selected", self.selectedSubject)
        game = self.Game
        if self.UI < 0:
            pass
        elif self.UI == 0:
            self.resetCardColors()
            if selectedSubject == "Board":  #Weapon won't be resolved by this functioin. It automatically cancels selection
                print("Board is not a valid subject.")
                self.cancelSelection()
            elif selectedSubject == "TurnEnds":
                self.cancelSelection()
                self.subject, self.target = None, None
                self.executeGamePlay(lambda: game.switchTurn(), isEndTurn=True)
            elif entity.camp != game.turn or (0 < self.camp != entity.camp):
                print("You can only select your own characters as subject.")
                self.cancelSelection()
            else:  #选择的是我方手牌、我方英雄、我方英雄技能、我方场上随从，
                self.subject, self.target = entity, None
                self.selectedSubject = selectedSubject
                self.UI, self.choice = 2, 0  #选择了主体目标，则准备进入选择打出位置或目标界面。抉择法术可能会将界面导入抉择界面。
                button.selected = 1 - button.selected
                if self.arrow:
                    self.arrow.removeNode()
                    self.arrow = None
                if selectedSubject.endswith("inHand"):  #Choose card in hand as subject
                    if not game.Manas.affordable(entity):  #No enough mana to use card
                        self.cancelSelection()
                    else:  #除了法力值不足，然后是指向性法术没有合适目标和随从没有位置使用
                        typewhenPlayed = self.subject.getTypewhenPlayed()
                        if typewhenPlayed == "Spell" and not entity.available():
                            #法术没有可选目标，或者是不可用的非指向性法术
                            self.cancelSelection()
                        elif game.space(entity.camp) < 1 and (typewhenPlayed == "Monster" or typewhenPlayed == "Amulet"):  #如果场上没有空位，且目标是护符或者无法触发激奏的随从的话，则不能打出牌
                            #随从没有剩余位置
                            self.cancelSelection()
                        else:  #Playable cards
                            if entity.need2Choose():
                                #所选的手牌不是影之诗卡牌，且我方有抉择全选的光环
                                if not entity.index.startswith("SV_"):
                                    if game.status[entity.camp]["Choose Both"] > 0:
                                        self.choice = -1  #跳过抉择，直接进入UI=1界面。
                                        if entity.needTarget(-1):
                                            self.highlightTargets(entity.findTargets("", self.choice)[0])
                                    else:  #Will conduct choose one
                                        self.UI = 1
                                        for i, option in enumerate(entity.options):
                                            pos = (4 + 8 * (i - 1), 45, -3 if entity.camp == 1 else 3)
                                            self.addinDisplayCard(option, pos=pos, scale=0.8, pickable=True)
                                elif entity.index.startswith("SV_"):
                                    self.UI = 1  #进入抉择界面，退出抉择界面的时候已经self.choice已经选好。
                                    return
                            else:  #No need to choose one
                                #如果选中的手牌是一个需要选择目标的SV法术
                                if entity.index.startswith("SV_") and typewhenPlayed == "Spell" and entity.needTarget():
                                    self.choice = -1  #影之诗因为有抉择不发动的情况，所以不能默认choice为0（炉石中的非抉择卡牌都默认choice=0），所以需要把choice默认为-1
                                    #需要目标选择的影之诗卡牌开始进入多个目标的选择阶段
                                    game.Discover.startSelect(entity, entity.findTargets("")[0])
                                    return
                                #选中的手牌是需要目标的炉石卡
                                #可以是任何类型的炉石卡
                                elif (typewhenPlayed not in ("Weapon", "Hero") and entity.needTarget()) or (typewhenPlayed == "Weapon" and entity.requireTarget):
                                    self.highlightTargets(entity.findTargets("", self.choice)[0])
                                    if typewhenPlayed != "Monster":
                                        print("The non-monster card you want to play requires an arrow")
                                        self.arrow = self.loader.loadModel("Models\\Arrow.glb")
                                        self.arrow.reparentTo(self.render)
                                        self.arrow.setPos(button.getPos())
                                        print("The arrow is ", self.arrow)
                                self.btnBeingDragged = button
                                print("Ready for drag")
                                print(self.btnBeingDragged, button.collNode)

                #不需目标的英雄技能当即使用。需要目标的进入目标选择界面。暂时不用考虑技能的抉择
                elif selectedSubject == "Power":
                    print("Check if can use power", entity)
                    if entity.name == "Evolve":
                        self.selectedSubject = "Power"
                        game.Discover.startSelect(entity, entity.findTargets("")[0])
                    #英雄技能会自己判定是否可以使用。
                    elif entity.needTarget():  #selectedSubject之前是"Hero Power 1"或者"Hero Power 2"
                        print("Power needs target")
                        self.selectedSubject = "Power"
                        self.highlightTargets(entity.findTargets("", self.choice)[0])
                        self.arrow = self.loader.loadModel("Models\\Arrow.glb")
                        self.arrow.reparentTo(self.render)
                        self.arrow.setPos(button.getPos())
                    else:
                        print("Request to use Hero Power {}".format(self.subject.name))
                        subject = self.subject
                        self.cancelSelection()
                        self.subject, self.target, self.UI = subject, None, -1
                        self.executeGamePlay(lambda: subject.use(None))
                        self.sendOwnMovethruServer() #In the 1P version, the sendOwnMovethruServer is blank anyways
                #不能攻击的随从不能被选择。
                elif selectedSubject.endswith("onBoard"):
                    if not entity.canAttack():
                        self.cancelSelection()
                    else:
                        self.highlightTargets(entity.findBattleTargets()[0])
                        self.arrow = self.loader.loadModel("Models\\Arrow.glb")
                        self.arrow.reparentTo(self.render)
                        self.arrow.setPos(button.getPos())
        elif self.UI == 1:  #在抉择界面下点击了抉择选项会进入此结算流程
            if self.arrow:
                self.arrow.removeNode()
                self.arrow = None
            if selectedSubject == "ChooseOneOption" and entity.available():
                if self.subject.index.startswith("SV_"):  #影之诗的卡牌的抉择选项确定之后进入与炉石卡不同的UI
                    index = self.subject.options.index(entity)
                    self.UI, self.choice = 2, index
                    for option in self.subject.options:
                        print("Removing the choose one option", option, option.btn)
                        self.removeBtn(option.btn)
                    if self.subject.needTarget(self.choice):
                        self.highlightTargets(self.subject.findTargets("", self.choice)[0])
                else:  #炉石卡的抉择选项确定完毕
                    #The first option is indexed as 0.
                    index = self.subject.options.index(entity)
                    self.UI, self.choice = 2, index
                    for option in self.subject.options:
                        self.removeBtn(option.btn)
                    if self.subject.needTarget(self.choice) and self.subject.type == "Spell":
                        self.highlightTargets(self.subject.findTargets("", self.choice)[0])
                        self.arrow = self.loader.loadModel("Models\\Arrow.glb")
                        self.arrow.reparentTo(self.render)
                        self.arrow.setPos(button.getPos())
                    else:
                        self.btnBeingDragged = self.subject.btn
                        print("Ready for drag")
            elif selectedSubject == "TurnEnds":
                self.cancelSelection()
                self.subject, self.target = None, None
                self.executeGamePlay(lambda: game.switchTurn(), isEndTurn=True)
            else:
                print("You must click an available option to continue.")
        #炉石的目标选择在此处进行
        elif self.UI == 2:  #影之诗的目标选择是不会进入这个阶段的，直接进入UI == 3，并在那里完成所有的目标选择
            self.target = entity
            print("Selected target: {}".format(entity))
            #No matter what the selections are, pressing EndTurn button ends the turn.
            #选择的主体是场上的随从或者英雄。之前的主体在UI=0的界面中已经确定一定是友方角色。
            if selectedSubject == "TurnEnds":
                self.cancelSelection()
                self.subject, self.target = None, None
                self.executeGamePlay(lambda: game.switchTurn(), isEndTurn=True)
                self.sendEndTurnthruServer()  #In the 1P version, the sendEndTurnthruServer is blank anyways
            elif selectedSubject.endswith("inHand"):  #影之诗的目标选择不会在这个阶段进行
                self.cancelSelection()
            elif self.selectedSubject.endswith("onBoard"):  #已经选择了一个场上的角色，随从或英雄
                if "Hero" not in selectedSubject and selectedSubject != "MonsteronBoard":
                    print("Not attackable chars for monster attack, e.g. Dormant")
                else:
                    print("Requesting battle: {} attacks {}".format(self.subject.name, entity))
                    subject, target = self.subject, self.target
                    self.cancelSelection()
                    self.subject, self.target, self.UI = subject, target, -1
                    self.executeGamePlay(lambda: game.battle(subject, target))
                    self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
            #手中选中的随从在这里结算打出位置，如果不需要目标，则直接打出。
            #假设有时候选择随从的打出位置时会有鼠标刚好划过一个随从的情况
            elif self.selectedSubject == "MonsterinHand" or self.selectedSubject == "AmuletinHand":  #选中场上的友方随从，我休眠物和护符时会把随从打出在其左侧
                if selectedSubject == "Board" or (entity.camp == self.subject.camp and (selectedSubject.endswith("onBoard") and not selectedSubject.startswith("Hero"))):
                    self.selectedSubject = "MonsterPosDecided"  #将主体记录为标记了打出位置的手中随从。
                    #抉择随从如有全选光环，且所有选项不需目标，则直接打出。 连击随从的needTarget()由连击条件决定。
                    #print("Monster {} in hand needs target: {}".format(self.subject.name, self.subject.needTarget(self.choice)))
                    if not (self.subject.needTarget(self.choice) and self.subject.targetExists(self.choice)):
                        #print("Requesting to play monster {} without target. The choice is {}".format(self.subject.name, self.choice))
                        subject, position, choice = self.subject, self.pos, self.choice
                        self.cancelSelection()
                        self.subject, self.target, self.UI = subject, None, -1
                        self.executeGamePlay(lambda: game.playMonster(subject, None, position, choice))
                        self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
                    else:  #随从打出后需要目标
                        #print("The monster requires target to play. needTarget() returns {}".format(self.subject.needTarget(self.choice)))
                        #需要区分SV和炉石随从的目标选择。
                        subject = self.subject
                        #如果是影之诗随从，则需要进入多个目标选择的UI==3阶段，而炉石随从则仍留在该阶段之路等待单目标选择的完成
                        if subject.index.startswith("SV_"):  #能到这个阶段的都是有目标选择的随从
                            self.choice = 0
                            game.Discover.startSelect(subject, subject.findTargets("")[0])
                        btn_PlayedMonster = self.subject.btn
                        self.arrow = self.loader.loadModel("Models\\Arrow.glb")
                        self.arrow.reparentTo(self.render)
                        self.arrow.setPos(btn_PlayedMonster.getPos())
            #随从的打出位置和抉择选项已经在上一步选择，这里处理目标选择。
            elif self.selectedSubject == "MonsterPosDecided":
                if selectedSubject == "MonsteronBoard" or selectedSubject == "HeroonBoard":
                    print("Requesting to play monster {}, targeting {} with choice: {}".format(self.subject.name, entity.name, self.choice))
                    subject, position, choice = self.subject, self.pos, self.choice
                    self.cancelSelection()
                    self.subject, self.target, self.UI = subject, entity, -1
                    self.executeGamePlay(lambda: game.playMonster(subject, entity, position, choice))
                    self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
                else:
                    print("Not a valid selection. All selections canceled.")
            #选中的法术已经确定抉择选项（如果有），下面决定目标选择。
            elif self.selectedSubject == "SpellinHand":
                if not self.subject.needTarget(self.choice):  #Non-targeting spells can only be cast by clicking the board
                    if "Board" in selectedSubject:  #打出非指向性法术时，可以把卡牌拖动到随从，英雄或者桌面上
                        print("Requesting to play spell {} without target. The choice is {}".format(self.subject.name, self.choice))
                        subject, target, choice = self.subject, None, self.choice
                        self.cancelSelection()
                        self.subject, self.target, self.UI = subject, target, -1
                        self.executeGamePlay(lambda: game.playSpell(subject, target, choice))
                        self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
                else:  #法术或者法术抉择选项需要指定目标。
                    if selectedSubject == "MonsteronBoard" or selectedSubject == "HeroonBoard":
                        print("Requesting to play spell {} with target {}. The choice is {}".format(self.subject.name, entity, self.choice))
                        subject, target, choice = self.subject, entity, self.choice
                        self.cancelSelection()
                        self.subject, self.target, self.UI = subject, target, -1
                        self.executeGamePlay(lambda: game.playSpell(subject, target, choice))
                        self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
                    else:
                        print("Targeting spell must be cast on Hero or Monster on board.")
            #选择手牌中的武器的打出目标
            elif self.selectedSubject == "WeaponinHand":
                if not self.subject.requireTarget:
                    if selectedSubject == "Board":
                        print("Requesting to play Weapon {}".format(self.subject.name))
                        subject, target = self.subject, None
                        self.cancelSelection()
                        self.subject, self.target, self.UI = subject, None, -1
                        self.executeGamePlay(lambda: game.playWeapon(subject, None))
                        self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
                else:
                    if selectedSubject == "MonsteronBoard" or selectedSubject == "HeroonBoard":
                        subject, target = self.subject, entity
                        print("Requesting to play weapon {} with target {}".format(subject.name, target.name))
                        self.cancelSelection()
                        self.subject, self.target, self.UI = subject, target, -1
                        self.executeGamePlay(lambda: game.playWeapon(subject, target))
                        self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
                    else:
                        print("Targeting weapon must be played with a target.")
            #手牌中的英雄牌是没有目标的
            elif self.selectedSubject == "HeroinHand":
                if selectedSubject == "Board":
                    print("Requesting to play hero card %s" % self.subject.name)
                    subject = self.subject
                    self.cancelSelection()
                    self.subject, self.target, self.UI = subject, None, -1
                    self.executeGamePlay(lambda: game.playHero(subject))
                    self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
            #Select the target for a Hero Power.
            #在此选择的一定是指向性的英雄技能。
            elif self.selectedSubject == "Power":  #如果需要指向的英雄技能对None使用，HeroPower的合法性检测会阻止使用。
                if selectedSubject == "MonsteronBoard" or selectedSubject == "HeroonBoard":
                    print("Requesting to use Hero Power {} on {}".format(self.subject.name, entity.name))
                    subject = self.subject
                    self.cancelSelection()
                    self.subject, self.target, self.UI = subject, entity, -1
                    self.executeGamePlay(lambda: subject.use(entity))
                    self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
                else:
                    print("Targeting hero power must be used with a target.")
        else:  #self.UI == 3
            if selectedSubject == "DiscoverOption":
                self.UI = 0
                self.discover = entity
            elif selectedSubject == "SelectObj":
                # print("Selecting obj for SV card")
                self.choice += 1
                self.subject.targets.append(entity)
                try:
                    self.target.append(entity)
                except:
                    self.target = [entity]
                if self.subject.needTarget():
                    game.Discover.startSelect(self.subject, self.subject.findTargets("", self.choice)[0])
                else:  #如果目标选择完毕了，则不用再选择，直接开始打出结算
                    self.UI = 0
                    subject, target, position, choice = self.subject, self.subject.targets, self.pos, -1
                    print("Requesting to play Shadowverse spell {} with targets {}".format(subject.name, target))
                    self.cancelSelection()
                    func = {"Monster": lambda: game.playMonster(subject, target, position, choice),
                            "Spell": lambda: game.playSpell(subject, target, choice),
                            "Amulet": lambda: game.playAmulet(subject, target, choice),
                            "Power": lambda: subject.use(target, choice),
                            }[subject.type]
                    self.executeGamePlay(func)
                    self.sendOwnMovethruServer() #In the 1P version, the sendEndTurnthruServer is blank anyways
            elif selectedSubject == "Fusion":
                self.UI = 0
                self.update(all=False, hand=True)
                game.Discover.initiator.fusionDecided(entity)
            else:
                print("You MUST click a correct object to continue.")



    def playanimSummon(self,card:CardData,pos):
        en:CardEntityCE=self.spaceCE.createEn("CardEntity",pos,0)
        card.entityID=en.id
        en.initCardEntity(card)
        en.playanimSummon(card)
        pass

    def playanimMonsterAttack(self):
        pass



    def playanimToPhase(self,side,phase):
        for s,avatar in self.avatars.items():
            avatar.playanimDraw1Card()



    # def prepareDeckBuilderPanel(self): pass
    #
    # # Load the board, turnEndButton, manaModels and arrow
    # def loadBackground(self):
    #     if not self.btnBoard:  # Loaded models can be reused
    #         plane = self.loader.loadModel("Models\\BoardModels\\Background.glb")
    #         #plane.setTexture(plane.findTextureStage('*'),
    #         #				 self.loader.loadTexture("Models\\BoardModels\\%s.png" % self.boardID), 1)
    #         plane.name = "Model2Keep_Board"
    #         plane.reparentTo(self.render)
    #         plane.setPos(0, 0, 1)
    #         (cNode := CollisionNode("cNode")).addSolid(CollisionBox((0, 0.4, -0.2), 14.5, 7.5, 0.2))
    #         plane.attachNewNode(cNode)#.show()
    #         self.btnBoard = Btn_Board(self, plane)
    #         plane.setPythonTag("btn", self.btnBoard)
    #     else:
    #         self.btnBoard.np.setTexture(self.btnBoard.np.findTextureStage('*'),
    #                                     self.loader.loadTexture("Models\\BoardModels\\%s.png" % self.boardID), 1)
    #     # Load the turn end button
    #     if not self.btnTurnEnd:
    #         turnEnd = self.loader.loadModel("Models\\BoardModels\\TurnEndButton.glb")
    #         turnEnd.reparentTo(self.render)
    #         turnEnd.name = "Model2Keep_TurnEndBtn"
    #         turnEnd.setPos(TurnEndBtn_Pos)
    #         (cNode := CollisionNode("cNode")).addSolid(CollisionBox((0, 0, 0), 2, 1, 0.2))
    #         turnEnd.attachNewNode(cNode)#.show()
    #         self.btnTurnEnd = Btn_TurnEnd(self, turnEnd)
    #         turnEnd.setPythonTag("btn", self.btnTurnEnd)
    #
    #     # The fatigue model to show when no more card to draw
    #     if not self.np_Fatigue:
    #         self.np_Fatigue = self.loader.loadModel("Models\\BoardModels\\Fatigue.glb")
    #         self.np_Fatigue.setTexture(self.np_Fatigue.findTextureStage('0'),
    #                                    self.loader.loadTexture("Models\\BoardModels\\Fatigue.png"), 1)
    #         self.np_Fatigue.name = "Model2Keep_Fatigue"
    #         self.np_Fatigue.reparentTo(self.render)
    #         self.np_Fatigue.setPos(4, 0, 0)
    #         makeText(self.np_Fatigue, "Fatigue", valueText='1', pos=(-0.03, -1.3, 0.1),
    #                  scale=1, color=red, font=self.getFont())
    #
    #     if not self.np_YourTurnBanner:
    #         self.np_YourTurnBanner = self.loader.loadModel("Models\\BoardModels\\YourTurnBanner.glb")
    #         self.np_YourTurnBanner.name = "Model2Keep_YourTurnBanner"
    #         self.np_YourTurnBanner.setTexture(self.np_YourTurnBanner.findTextureStage("*"),
    #                                           self.loader.loadTexture("Models\\BoardModels\\ForBanner.png"), 1)
    #         self.np_YourTurnBanner.reparentTo(self.render)
    #
    #     if not self.arrow:
    #         self.arrow = model = self.loader.loadModel("Models\\Arrow.glb")
    #         model.setTexture(model.findTextureStage('0'), self.loader.loadTexture("Models\\Arrow.png"), 1)
    #         model.reparentTo(self.render)
    #         model.name = "Model2Keep_Arrow"
    #         model.hide()
    #
    #     if not self.crosshair:
    #         self.crosshair = model = self.loader.loadModel("Models\\Crosshair.glb")
    #         model.setTexture(model.findTextureStage('0'), self.loader.loadTexture("Models\\Arrow.png"), 1)
    #         model.reparentTo(self.render)
    #         model.name = "Model2Keep_Crosshair"
    #         model.hide()
    #
    #     if not self.manaModels:
    #         for name in ("Mana", "EmptyMana", "LockedMana", "OverloadedMana"):
    #             model = self.loader.loadModel("Models\\BoardModels\\Mana.glb")
    #             model.name = "Model2Keep_" + name
    #             model.reparentTo(self.render)
    #             model.setTexture(model.findTextureStage('*'),
    #                              self.loader.loadTexture("Models\\BoardModels\\%s.png" % name), 1)
    #             self.manaModels[name] = [model]
    #             for i in range(9):
    #                 self.manaModels[name].append(model.copyTo(self.render))
    #
    # def relocateCamera(self):
    #     self.camLens.setFov(51.1, 27.5)
    #     self.cam.setPosHpr(0, 0, CamPos_Z, 0, -90, 0)
    #     props = WindowProperties()
    #     props.setSize(w, h)
    #     self.win.requestProperties(props)
    #
    # def getDegreeDistance_fromCoors(self, x_0, y_0, x_1, y_1):
    #     distance = numpy.sqrt((x_1 - x_0) ** 2 + (y_1 - y_0) ** 2)
    #     degree = 180 * numpy.arccos((x_1 - x_0) / distance) / numpy.pi
    #     if y_1 < y_0: degree = 360 - degree
    #     return degree - 90, distance

    """Handle animation of game display and mulligan. To be invoked by both Run_1PGame and Run_OnlineGame"""
    # def initGameDisplay(self):
    #     for ID in (1, 2):
    #         self.deckZones[ID].draw(len(self.Game.Hand_Deck.decks[ID]), len(self.Game.Hand_Deck.hands[ID]))
    #         self.heroZones[ID].drawMana(self.Game.Manas.manas[ID], self.Game.Manas.manasUpper[ID],
    #                                     self.Game.Manas.manasLocked[ID], self.Game.Manas.manasOverloaded[ID])
    #         self.heroZones[ID].placeCards()

    #init all
    # def initMulliganDisplay(self, for1P):
    #     self.handZones = {1: HandZone(self, 1), 2: HandZone(self, 2)}
    #     self.minionZones = {1: MinionZone(self, 1), 2: MinionZone(self, 2)}
    #     self.heroZones = {1: HeroZone(self, 1), 2: HeroZone(self, 2)}
    #     self.historyZone = HistoryZone(self)
    #     if not self.deckZones:
    #         self.deckZones = {1: DeckZone(self, 1), 2: DeckZone(self, 2)}
    #     elif not for1P:
    #         self.deckZones[self.ID].changeSide(self.ID)
    #         self.deckZones[3 - self.ID].changeSide(3 - self.ID)
    #
    #     self.mulliganStatus = {1: [0, 0, 0], 2: [0, 0, 0, 0]}  # 需要在每次退出和重新进入时刷新
    #     self.stage = -1
    #     self.initGameDisplay()
    #     self.addaButton("Button_InGame", "StartMulligan", self.render, pos=(0, 0, 10) if for1P else (0, -4, 10),
    #                     removeAfter=True, func=self.initMulligan)
    #
    #     # Draw the animation of mulligan cards coming out of the deck
    #     if for1P: sides, Y_1, Y_2 = (1, 2), -3.3, 6
    #     else: sides, Y_1, Y_2 = (self.ID,), 1.5, 1.5
    #     self.posMulligans = {1: [(-7, Y_1, 10), (0, Y_1, 10), (7, Y_1, 10)],
    #                          2: [(-8.25, Y_2, 10), (-2.75, Y_2, 10), (2.75, Y_2, 10), (8.25, Y_2, 10)]}
    #     for ID in sides: self.initMulligan_OutofDeck(ID)
    #
    #     # for child in self.render.getChildren():
    #     # 	if "2Keep" not in child.name: print("After initGame, left in render:", child.name, type(child))
    #
    #     print("Own sock_Recv&sock_Send is", self.sock_Recv, self.sock_Send)

    # def initMulligan(self, btn): pass

    # def initMulligan_OutofDeck(self, ID):
    #     deckZone, handZone, i = self.deckZones[ID], self.handZones[ID], 0
    #     pos_0, hpr_0 = deckZone.pos, (90, 90, 0)
    #     cards2Mulligan = self.Game.mulligans[ID]
    #     mulliganBtns = []
    #     for card, pos, hpr, scale in zip(cards2Mulligan, [pos_0]*len(cards2Mulligan), [hpr_0]*len(cards2Mulligan),
    #                                      [1]*len(cards2Mulligan)):
    #         mulliganBtns.append(genCard(self, card, isPlayed=False, pos=pos, hpr=hpr, scale=scale)[1])
    #     for btn, pos in zip(mulliganBtns, self.posMulligans[ID]):
    #         Sequence(Wait(0.4 + i * 0.4),
    #                  LerpPosHprScaleInterval(btn.np, duration=0.5, pos=pos, hpr=(0, 0, 0), scale=1)).start()
    #         i += 1

    # def replaceMulligan_PrepSeqHolder(self, addCoin, for1P, ID):
    #     # At this point, the Coin is added to the Game.mulligans[2]
    #     if addCoin: genCard(self, card=self.Game.mulligans[2][-1], isPlayed=False, pos=(13.75, 6 if for1P else 1.5, 10))
    #
    #     para = Parallel()
    #     for ID in (1, 2) if for1P else (ID,):
    #         posMulligans = self.posMulligans[ID]
    #         pos_DeckZone, hpr_0 = self.deckZones[ID].pos, (90, 90, 0)
    #         for i, card in enumerate(self.Game.mulligans[ID]):
    #             if not card.btn:  # 把替换后新摸到的牌画在牌库位置并添加运动到调度位置的动画
    #                 np, btn = genCard(self, card, isPlayed=False, pos=pos_DeckZone, hpr=hpr_0, scale=1)
    #                 para.append(LerpPosHprScaleInterval(np, duration=0.5, pos=posMulligans[i], hpr=(0, 0, 0), scale=1))
    #     if for1P:
    #         self.seqHolder = [Sequence(para, Wait(1))]
    #         self.seqReady = False
    #     else: para.start()
    #
    # # 在决定完手牌中的牌以及它们的可能变形之后，添加它们的变形动画和移入手牌区动画
    # def mulligan_TransformandMoveCards2Hand(self, cardsChanged, cardsNew):
    #     handZone_1, handZone_2, HD = self.handZones[1], self.handZones[2], self.Game.Hand_Deck
    #     seq = self.seqHolder[-1]
    #
    #     seq.append(Func(self.deckZones[1].draw, len(HD.decks[1]), len(HD.hands[1])))
    #     seq.append(Func(self.deckZones[2].draw, len(HD.decks[2]), len(HD.hands[2])))
    #     seq.append(Wait(0.4))
    #     seq.append(Parallel(handZone_1.placeCards(False), handZone_2.placeCards(False)))
    #     if cardsChanged: seq.append(Func(handZone_1.transformHands([card.btn for card in cardsChanged], cardsNew)))
    #
    # """Animation control setup"""
    def keepExecutingGamePlays(self):
        if self.gamePlayQueue:#不断执行
            a=self.gamePlayQueue.pop(0)
            # print("gameplayee ",a.__name__)
            a()
            self.cancelSelection()
    #
    # def highlightTargets(self, legalTargets):
    #     game = self.Game
    #     for ID in (1, 2):
    #         for card in game.minions[ID] + game.Hand_Deck.hands[ID] + [game.heroes[ID]]:
    #             card.btn.np.setColor(white if card in legalTargets else grey)
    #
    def resetCardColors(self):
        return
        game = self.Game
        for ID in (1, 2):
            for card in game.monsters[ID] + game.Hand_Deck.hands[ID] + [game.heroes[ID]]:
                if card and card.btn and card.btn.np:
                    card.btn.np.setColor(white)
                else: print("Reset color fail", card, card.btn)
    #
    # def resetSubTarColor(self, subject=None, target=None):
    #     seq = self.seqHolder[-1]
    #     if subject:  # If subject not given, leave self.subject and its color unchanged
    #         if self.subject and self.subject.btn: seq.append(Func(self.subject.btn.setBoxColor, transparent))
    #         self.subject = subject
    #         if subject.btn: seq.append(Func(subject.btn.setBoxColor, yellow))
    #     if self.target:  # 先取消当前的所有target颜色显示，之后重新根据target显示
    #         for obj in self.target:
    #             if obj.btn: seq.append(Func(obj.btn.setBoxColor, transparent))
    #         self.target = []
    #     if target:
    #         self.target = target = list(target) if isinstance(target, (list, tuple)) else [target]
    #         for obj in target:
    #             if obj.btn: seq.append(Func(obj.btn.setBoxColor, pink))
    #     if subject or target: seq.append(Wait(0.15))
    #
    # # 游戏在逻辑结算完毕之后会直接先进行一次各卡牌的颜色处理，从而让玩家在打出一张牌之后马上知道场上已有的卡牌的状态
    # # 在一些目标指向过程中可以改变subject和target的颜色，从而指示目标的变化
    # # GUI在一次操作的动画流程即将结束时也会进行一次处理，从而让玩家知道所有新出现的卡牌的状态
    # def decideCardColors(self):
    #     game = self.Game
    #     for card in game.Hand_Deck.hands[1] + game.Hand_Deck.hands[2]:
    #         card.effCanTrig()
    #         card.checkEvanescent()
    #     curTurn = game.turn
    #     for ID in (1, 2):
    #         # 双人对战过程中对方的牌不展示的情况下不显示可选框，其他情况下均显示
    #         if self.sock_Send:
    #             showCardColor = ID == curTurn and (ID == self.ID or self.showEnemyHand)
    #         else:
    #             showCardColor = ID == curTurn
    #         canTrade = game.Manas.manas[ID] > 0 and game.Hand_Deck.decks[ID]
    #         for card in game.Hand_Deck.hands[ID]:
    #             if card.btn:
    #                 card.btn.setBoxColor(card.btn.decideColor() if showCardColor else transparent)
    #                 if "~Tradeable" in card.index and (np_Trade := card.btn.np.find("Trade")):
    #                     box = np_Trade.find("box")
    #                     if showCardColor and canTrade:
    #                         box.show()
    #                         box.setColor(green)
    #                     else: box.hide()
    #         for card in game.minions[ID]:
    #             if card.btn: card.btn.setBoxColor(card.btn.decideColor() if showCardColor else transparent)
    #         hero, power = game.heroes[ID], game.powers[ID]
    #         if hero.btn: hero.btn.setBoxColor(hero.btn.decideColor() if showCardColor else transparent)
    #         if power.btn: power.btn.setBoxColor(power.btn.decideColor() if showCardColor else transparent)
    #     self.btnTurnEnd.changeDisplay(jobDone=curTurn == self.ID and not game.morePlaysPossible())
    def decideCardColors(self):
        pass
    #
    # """Animation details"""
    # # Card/Hand animation
    # def putaNewCardinHandAni(self, card):
    #     genCard(self, card, isPlayed=False, onlyShowCardBack=self.need2Hide(card))
    #     self.handZones[card.ID].placeCards()
    #
    # def cardReplacedinHand_Refresh(self, card):
    #     genCard(self, card, isPlayed=False, onlyShowCardBack=self.need2Hide(card))
    #     self.handZones[card.ID].placeCards()
    #
    # def transformAni(self, target, newCard, onBoard):
    #     if not isinstance(target, (list, tuple)): target, newCard = (target,), (newCard,)
    #     self.seqHolder[-1].append(para := Parallel())
    #     for obj, newObj in zip(target, newCard):
    #         if obj.btn and obj.btn.np:
    #             np_New, btn_New = genCard(self, newObj, isPlayed=onBoard, pickable=True, onlyShowCardBack=obj.btn.onlyCardBackShown)
    #             para.append(Func(self.replaceaNPwithNewCard, obj.btn.np, btn_New, not self.need2Hide(obj), 1.9 if onBoard else 2.3))
    #
    # def replaceaNPwithNewCard(self, npOld, btnNew, mist=True, mistScale=1.9):
    #     nodePathNew = btnNew.np
    #     texCard, seqNode = makeTexCard(self, filePath="TexCards\\Shared\\TransformMist.egg",
    #                                    pos=(0, 0, 0.2), scale=mistScale, parent=nodePathNew)
    #     Sequence(Func(seqNode.play), Wait(0.75), Func(texCard.removeNode)).start()
    #     nodeOld, nodeNew = npOld.node(), nodePathNew.node()
    #     oldChildren = npOld.getChildren()
    #     nodeNew.replaceNode(nodeOld)
    #     for child in oldChildren:
    #         child.removeNode()
    #     btnNew.np = npOld
    #     npOld.setPythonTag("btn", btnNew)
    #
    # def transformAni_inHand(self, target, newCard):
    #     texCard = seqNode = None
    #     if not self.need2Hide(target):
    #         texCard, seqNode = makeTexCard(self, filePath="TexCards\\Shared\\TransformMist.egg",
    #                                        pos=(0, 0, 0.2), scale=2.3)
    #     seq_Holder = self.seqHolder[-1]
    #     if target.category == newCard.category:
    #         newCard.btn = target.btn
    #         if texCard:
    #             seq_Holder.append(Sequence(Func(texCard.reparentTo, target.btn.np), Func(seqNode.play), Wait(0.05),
    #                                        Func(target.btn.changeCard, newCard, False)))
    #             seq_Holder.append(Func(Sequence(Wait(0.75), Func(texCard.removeNode)).start))
    #         else:
    #             seq_Holder.append(Func(target.btn.changeCard, newCard, False))
    #         target.btn = None
    #     else:
    #         np_New, btn_New = genCard(self, newCard, isPlayed=False, pickable=True,
    #                                   onlyShowCardBack=target.btn.onlyCardBackShown)
    #         np_Old = target.btn.np
    #         if texCard:
    #             seq_Holder.append(Sequence(Func(texCard.reparentTo, np_Old), Func(seqNode.play), Wait(0.05),
    #                                        Func(np_New.reparentTo, np_Old), Wait(0.75),
    #                                        Func(np_New.wrtReparentTo, self.render),
    #                                        Func(np_Old.removeNode))
    #                               )
    #         else:
    #             seq_Holder.append(Func(np_New.reparentTo, np_Old), Func(np_New.wrtReparentTo, self.render),
    #                               Func(np_Old.removeNode))
    #
    # def transformAni_onBoard(self, target, newCard):
    #     newCard.btn = target.btn
    #     texCard = seqNode = None
    #     if target.category == newCard.category and target.category in ("Minion", "Weapon"):
    #         texCard, seqNode = makeTexCard(self, filePath="TexCards\\Shared\\TransformMist.egg",
    #                                        pos=(0, 0, 0.2), scale=1.9)
    #     seq_Holder = self.seqHolder[-1]
    #     if not texCard:
    #         seq_Holder.append(Func(target.btn.changeCard, newCard, True))
    #     else:
    #         seq_Holder.append(Sequence(Func(texCard.reparentTo, target.btn.np), Func(seqNode.play), Wait(0.05),
    #                                    Func(target.btn.changeCard, newCard, True)))
    #         seq_Holder.append(Func(Sequence(Wait(0.65), Func(texCard.removeNode)).start))
    #     target.btn = None
    #
    # # 因为可以结算的时候一般都是手牌已经发生了变化，所以只能用序号来标记每个btn了
    # # linger is for when you would like to see the card longer before it vanishes
    # def cardsLeaveHandAni(self, cards, ID=0, enemyCanSee=True, linger=False):
    #     handZone, para, btns2Destroy = self.handZones[ID], Parallel(), [card.btn for card in cards]
    #     # 此时需要离开手牌的牌已经从Game.Hand_Deck.hands里面移除,手牌列表中剩余的就是真实存在还在手牌中的
    #     for btn, card in zip(btns2Destroy, cards):
    #         seq, nodePath = Sequence(), btn.np
    #         if enemyCanSee and btn.onlyCardBackShown:
    #             seq.append(Func(btn.changeCard, card, False, False))
    #         x, y, z = nodePath.getPos()
    #         if not -9 < y < 9:
    #             y = DiscardedCard1_Y if self.ID == btn.card.ID else DiscardedCard2_Y
    #             seq.append(LerpPosHprInterval(nodePath, duration=0.3, pos=(x, y, z), startHpr=(0, 0, 0), hpr=(0, 0, 0)))
    #             seq.append(Wait(0.6))
    #         # 如果linger为True就留着这张牌的显示，到之后再处理
    #         if not linger: seq.append(Func(nodePath.detachNode))
    #         para.append(seq)
    #     handZone.placeCards()
    #     self.seqHolder[-1].append(para)
    #
    # def hand2BoardAni(self, card):
    #     ID = card.ID
    #     handZone, minionZone = self.handZones[ID], self.minionZones[ID]
    #     # At this point, minion has been inserted into the minions list. The btn on the minion won't change. It will simply change "isPlayed"
    #     ownMinions = self.Game.minions[ID]
    #     x, y, z = posMinionsTable[minionZone.y][len(ownMinions)][ownMinions.index(card)]
    #     # Must be first set to isPlayed=True, so that ensuing statChangeAni can correctly respond
    #     if card.btn.onlyCardBackShown:
    #         self.seqHolder[-1].append(Func(card.btn.changeCard, card, False, True))
    #     card.btn.isPlayed = True  # Must be first set to isPlayed=True, so that ensuing statChangeAni can correctly respond
    #     card.btn.reassignBox()
    #     seq = Sequence(LerpPosHprScaleInterval(card.btn.np, duration=0.25, pos=(x, y, z + 5), hpr=(0, 0, 0), startHpr=(0, 0, 0),
    #                                            scale=scale_Minion),
    #                    Func(card.btn.changeCard, card, True),
    #                    Parallel(minionZone.placeCards(False), handZone.placeCards(False)), name="Hand2Board Ani")
    #     self.seqHolder[-1].append(seq)
    #
    # def board2HandAni(self, card):
    #     handZone, minionZone = self.handZones[card.ID], self.minionZones[card.ID]
    #     # At this point, minion has been extracted from the minion lists
    #     ownMinions, ownHands = self.Game.minions[card.ID], self.Game.Hand_Deck.hands[card.ID]
    #     x, y, z = card.btn.np.getPos()
    #     onlyShowCardBack = self.need2Hide(card)
    #     card.btn.isPlayed = True  # Must be first set to isPlayed=True, so that ensuing statChangeAni can correctly respond
    #     card.btn.reassignBox()
    #     seq = Sequence(LerpPosInterval(card.btn.np, duration=0.25, pos=Point3(x, y, z + 5)),
    #                    Wait(0.15), Func(card.btn.changeCard, card, False, True, onlyShowCardBack), Wait(0.2),
    #                    Func(self.deckZones[self.ID].draw, len(self.Game.Hand_Deck.decks[self.ID]), len(ownHands)),
    #                    Parallel(handZone.placeCards(False), minionZone.placeCards(False)),
    #                    name="Board 2 hand ani")
    #     self.seqHolder[-1].append(seq)
    #
    # def deck2BoardAni(self, card):
    #     ID = card.ID
    #     nodePath, btn = genCard(self, card,
    #                             isPlayed=False)  # place these cards at pos(0, 0, 0), to be move into proper position later
    #     # At this point, minion has been inserted into the minions list. The btn on the minion won't change. It will simply change "isPlayed"
    #     deckZone, minionZone = self.deckZones[ID], self.minionZones[ID]
    #     ownMinions = self.Game.minions[ID]
    #     x, y, z = posMinionsTable[minionZone.y][len(ownMinions)][ownMinions.index(card)]
    #     deckPos = Deck1_Pos if ID == self.ID else Deck2_Pos
    #     # The minion must be first set to isPlayed=True, so that the later statChangeAni can correctly respond
    #     btn.isPlayed = True
    #     card.btn.reassignBox()
    #     sequence = Sequence(Func(deckZone.draw, len(card.Game.Hand_Deck.decks[ID]), len(self.Game.Hand_Deck.hands[ID])),
    #                         LerpPosHprScaleInterval(nodePath, duration=0.3, startPos=deckPos, startHpr=hpr_Deck,
    #                                                 startScale=deckScale,
    #                                                 pos=(x, y, z + 5), hpr=(0, 0, 0), scale=scale_Minion),
    #                         Wait(0.2), Func(btn.changeCard, card, True),
    #                         minionZone.placeCards(False),
    #                         name="Deck to board Ani")
    #     self.seqHolder[-1].append(sequence)
    #
    # def revealaCardfromDeckAni(self, ID, index, bingo):
    #     card = self.Game.Hand_Deck.decks[ID][index]
    #     deckZone = self.deckZones[card.ID]
    #     pos_Pause = DrawnCard1_PausePos if self.ID == card.ID else DrawnCard2_PausePos
    #     nodePath, btn = genCard(self, card, isPlayed=False)  # the card is preloaded and positioned at (0, 0, 0)
    #     sequence = Sequence(Func(nodePath.setPosHpr, deckZone.pos, (90, 90, 0)),
    #                         Func(deckZone.draw, len(self.Game.Hand_Deck.decks[card.ID]),
    #                              len(self.Game.Hand_Deck.hands[card.ID])),
    #                         LerpPosHprScaleInterval(btn.np, duration=0.4, pos=pos_Pause, hpr=(0, 0, 0), scale=1,
    #                                                 blendType="easeOut"),
    #                         Wait(0.6)
    #                         )
    #     if bingo:
    #         sequence.append(LerpScaleInterval(nodePath, duration=0.2, scale=1.15))
    #         sequence.append(LerpScaleInterval(nodePath, duration=0.2, scale=1))
    #     sequence.append(
    #         LerpPosHprInterval(nodePath, duration=0.4, pos=deckZone.pos, hpr=(90, 90, 0), blendType="easeOut"))
    #     btn.add2Queue_NullifyBtnNodepath(sequence)  # 一般只有把卡牌洗回牌库时会有nodepath消失再出现的可能性
    #     sequence.append(Wait(0.2))
    #     self.seqHolder[-1].append(sequence)
    #
    # # Amulets and dormants also count as minions
    # def removeMinionorWeaponAni(self, card):
    #     if not (card.btn and card.btn.np): return
    #     # At this point, minion/dormant/weapon has left the containing list
    #     self.seqHolder[-1].append(Func(card.btn.np.detachNode))
    #     if card.category in ("Minion", "Dormant", "Amulet"):
    #         self.minionZones[card.ID].placeCards()
    #
    # # 直接出现，而不是从手牌或者牌库中召唤出来
    # def summonAni(self, card):
    #     # At this point, minion has been inserted into the minions list
    #     genCard(self, card, isPlayed=True)
    #     self.minionZones[card.ID].placeCards()
    #     self.seqHolder[-1].append(Wait(0.1))
    #
    # def weaponEquipAni(self, card):
    #     nodePath, btn = genCard(self, card, isPlayed=True)
    #     x, y, z = self.heroZones[card.ID].weaponPos
    #     self.seqHolder[-1].append(
    #         LerpPosHprInterval(nodePath, duration=0.3, startPos=(x, y + 0.2, z + 5), pos=(x, y, z), hpr=(0, 0, 0)))
    #
    # # 需要把secret原本的icon移除，然后加入卡牌
    # def secretDestroyAni(self, secrets, enemyCanSee=True):
    #     if secrets:
    #         heroZone = self.heroZones[secrets[0].ID]
    #         heroPos = heroZone.heroPos
    #         para_Remove = Parallel()
    #         for nodePath in [secret.btn.np for secret in secrets]: para_Remove.append(Func(nodePath.removeNode))
    #         self.seqHolder[-1].append(para_Remove)
    #
    #         if enemyCanSee:
    #             para_Show, para_RemoveCards, nps2Emerge, interval = Parallel(), Parallel(), [], 8
    #             for secret in secrets:
    #                 nps2Emerge.append(self.addCard(secret, pos=(heroPos[0], heroPos[1], 0), pickable=False)[0])
    #             leftMostX = interval * (len(secrets) - 1) / 2
    #             for i, nodePath in enumerate(nps2Emerge):
    #                 para_Show.append(
    #                     LerpPosHprScaleInterval(nodePath, duration=0.3, hpr=(0, 0, 0), startScale=0.1, scale=1,
    #                                             startPos=heroPos, pos=(leftMostX + interval * i, 1, ZoomInCard_Z)))
    #             for nodePath in nps2Emerge: para_RemoveCards.append(Func(nodePath.removeNode))
    #             self.seqHolder[-1].append(para_Show)
    #             self.seqHolder[-1].append(para_RemoveCards)
    #         heroZone.placeSecrets()
    #

    # def drawCardAni_LeaveDeck(self, card):
    #     deckZone = self.deckZones[card.ID]
    #     pos_Pause = DrawnCard1_PausePos if self.ID == card.ID else DrawnCard2_PausePos
    #     nodePath, btn = genCard(self, card, isPlayed=False, onlyShowCardBack=self.need2Hide(card))
    #     self.seqHolder[-1].append(Sequence(
    #         Func(deckZone.draw, len(self.Game.Hand_Deck.decks[card.ID]), len(self.Game.Hand_Deck.hands[card.ID])),
    #         Func(nodePath.setPosHpr, deckZone.pos, (90, 90, 0)),
    #         LerpPosHprScaleInterval(nodePath, duration=0.4, pos=pos_Pause, hpr=(0, 0, 0), scale=1, blendType="easeOut"),
    #         Wait(0.8))
    #     )
    #

    def playanimCardLeaveDeck(self,ID,card):
        pass


    # def drawCardAni_IntoHand(self, oldCard, newCard):
    #     btn = oldCard.btn
    #     handZone = self.handZones[oldCard.ID]
    #     if btn.card != newCard:
    #         print("Drawn card is changed", newCard)
    #         handZone.transformHands([btn], [newCard])
    #     handZone.placeCards()
    #     self.seqHolder[-1].append(Func(self.deckZones[oldCard.ID].draw, len(self.Game.Hand_Deck.decks[newCard.ID]),
    #                                    len(self.Game.Hand_Deck.hands[newCard.ID])))
    #

    def playanimDraw1Card(self,ID,card:Card):
        TEMP_MSG("duiel play draw 1 card")
        self.avatars[ID].playanimDraw1Card(card)
    # def millCardAni(self, card):
    #     deckZone = self.deckZones[card.ID]
    #
    #     pos_Pause = DrawnCard1_PausePos if self.ID == card.ID else DrawnCard2_PausePos
    #     nodePath, btn = genCard(self, card, isPlayed=False)
    #     interval = LerpPosHprScaleInterval(nodePath, duration=0.4, startPos=deckZone.pos, pos=pos_Pause,
    #                                        startHpr=(90, 90, 0), hpr=(0, 0, 0), scale=1, blendType="easeOut")
    #     texCard, seqNode = makeTexCard(self, "TexCards\\ForGame\\Mill.egg", scale=27)
    #     self.seqHolder[-1].append(
    #         Sequence(interval, Func(texCard.setPos, pos_Pause[0], pos_Pause[1] - 1, pos_Pause[2] + 0.4),
    #                  Func(seqNode.play), Wait(0.5), Func(nodePath.removeNode), Wait(0.5), Func(texCard.removeNode)))
    #
    # def cardLeavesDeckAni(self, card, enemyCanSee=True, linger=False):
    #     deckZone = self.deckZones[card.ID]
    #     pos_Pause = DrawnCard1_PausePos if self.ID == card.ID else DrawnCard2_PausePos
    #     nodePath, btn = genCard(self, card, isPlayed=False)  # the card is preloaded and positioned at (0, 0, 0)
    #     sequence = Sequence(Func(nodePath.setPosHpr, deckZone.pos, (90, 90, 0)),
    #                         Func(deckZone.draw, len(self.Game.Hand_Deck.decks[card.ID]),
    #                              len(self.Game.Hand_Deck.hands[card.ID])),
    #                         LerpPosHprScaleInterval(btn.np, duration=0.4, pos=pos_Pause, hpr=(0, 0, 0), scale=1,
    #                                                 blendType="easeOut"),
    #                         Wait(0.6))
    #     if not linger: sequence.append(Func(nodePath.removeNode))
    #     self.seqHolder[-1].append(sequence)
    #
    # def shuffleintoDeckAni(self, cards, enemyCanSee=True):
    #     ID = cards[0].ID
    #     deckZone = self.deckZones[ID]
    #     para, btns = Parallel(), []
    #     leftMostPos = -(len(cards) - 1) / 2 * 5
    #     for i, card in enumerate(cards):
    #         num = len(cards) - i
    #         if (btn := card.btn) and (nodePath := card.btn.np):  # For cards that already have btns and nodepaths.
    #             seq = Sequence(Wait(0.15 * num + 0.3),
    #                            LerpPosHprInterval(nodePath, duration=0.25, pos=deckZone.pos, hpr=(90, 90, 0)))
    #         else:  # For cards that are newly created
    #             nodePath, btn = genCard(self, card, isPlayed=False, pickable=False,
    #                                     onlyShowCardBack=not enemyCanSee and self.need2Hide(card))
    #             seq = Sequence(Func(nodePath.setPos, leftMostPos + 5 * i, 1.5, 8), Wait(0.15 * num + 0.3),
    #                            LerpPosHprInterval(nodePath, duration=0.2, pos=deckZone.pos, hpr=(90, 90, 0)))
    #         btn.add2Queue_NullifyBtnNodepath(seq)
    #         para.append(seq)
    #
    #     self.seqHolder[-1].append(para)
    #     self.seqHolder[-1].append(
    #         Func(deckZone.draw, len(self.Game.Hand_Deck.decks[ID]), len(self.Game.Hand_Deck.hands[ID])))
    #
    # def wait(self, duration=0, showLine=False):
    #     pass
    #
    # def offsetNodePath_Wait(self, nodePath, duration=0.3, dx=0, dy=0, dz=0, dh=0, dp=0, dr=0, add2Queue=True):
    #     if add2Queue:
    #         self.seqHolder[-1].append(Func(self.offsetNodePath, nodePath, duration, dx, dy, dz, dh, dp, dr))
    #         self.seqHolder[-1].append(Wait(duration))
    #     else: return self.offsetNodePath(nodePath, duration, dx, dy, dz, dh, dp, dr)
    #
    # def offsetNodePath(self, np, duration=0.3, dx=0, dy=0, dz=0, dh=0, dp=0, dr=0):
    #     x, y, z = np.getPos()
    #     h, p, r = np.getHpr()
    #     Sequence(LerpPosHprInterval(np, duration=duration, pos=(x+dx, y+dy, z+dz), hpr=(h+dh, p+dp, r+dr))).start()
    #
    # def moveNodePath2_wrt_Wait(self, np_2Move, np_Ref, duration=0.3, dx=0, dy=0, dz=0, add2Queue=True):
    #     if add2Queue:
    #         self.seqHolder[-1].append(Func(self.moveNodePath2_wrt, np_2Move, np_Ref, duration, dx, dy, dz))
    #         self.seqHolder[-1].append(Wait(duration))
    #     else: return Sequence(Func(self.moveNodePath2_wrt, np_2Move, np_Ref, duration, dx, dy, dz), Wait(duration))
    #
    # def moveNodePath2_wrt(self, np_2Move, nodePath_Ref, duration, dx, dy, dz):
    #     x, y, z = nodePath_Ref.getPos()
    #     Sequence(LerpPosInterval(np_2Move, duration=duration, pos=(x+dx, y+dy, z+dz))).start()
    #
    # def attackAni_HitandReturn(self, subject, target):
    #     np_Subject, np_Target = subject.btn.np, target.btn.np
    #     if subject.category == "Minion":
    #         ownMinions = self.Game.minions[subject.ID]
    #         x_0, y_0, z_0 = posMinionsTable[self.minionZones[subject.ID].y][len(ownMinions)][ownMinions.index(subject)]
    #     else:
    #         x_0, y_0, z_0 = self.heroZones[subject.ID].heroPos
    #     seq = Sequence(self.moveNodePath2_wrt_Wait(np_Subject, np_Target, duration=0.17, add2Queue=False),
    #                    LerpPosInterval(np_Subject, duration=0.17, pos=(x_0, y_0, z_0 + 3)),
    #                    LerpPosInterval(np_Subject, duration=0.15, pos=(x_0, y_0, z_0)),
    #                    )
    #     self.seqHolder[-1].append(seq)
    #
    # def attackAni_Cancel(self, subject):
    #     if subject.category == "Minion":
    #         minionZone, ownMinions = self.minionZones[subject.ID], self.Game.minions[subject.ID]
    #         if subject not in ownMinions: return
    #         pos_Orig = posMinionsTable[minionZone.y][len(ownMinions)][ownMinions.index(subject)]
    #     else:
    #         pos_Orig = self.heroZones[subject.ID].heroPos
    #
    #     self.seqHolder[-1].append(LerpPosInterval(subject.btn.np, duration=0.15, pos=pos_Orig))
    #
    # def battlecryAni(self, card):
    #     if card.btn:
    #         texCard, seqNode = makeTexCard(self, "TexCards\\For%ss\\Battlecry.egg" % card.category, pos=(0, 0.5, 0.03),
    #                                        scale=6)
    #         texCard.reparentTo(card.btn.np)
    #         self.seqHolder[-1].append(
    #             Func(Sequence(Func(seqNode.play, 0, 32), Wait(32 / 24), Func(texCard.removeNode)).start))
    #         self.seqHolder[-1].append(Wait(20 / 24))
    #
    # def heroExplodeAni(self, entities):
    #     for keeper in entities:
    #         if keeper.btn:
    #             texCard, seqNode = makeTexCard(self, "TexCards\\ForHeroes\\Breaking.egg",
    #                                            pos=(0, 0.2, 0.3), scale=5)
    #             texCard.reparentTo(keeper.btn.np)
    #             headPieces = self.loader.loadModel("Models\\HeroModels\\HeadPieces.glb")
    #             headPieces.reparentTo(self.render)
    #             headPieces.setTexture(headPieces.findTextureStage('*'),
    #                                   self.loader.loadTexture(
    #                                       "Images\\HeroesandPowers\\%s.png" % type(keeper).__name__), 1)
    #             x_0, y_0, z_0 = self.heroZones[keeper.ID].heroPos
    #             headPieces.setPos(x_0, y_0, z_0)
    #             para = Parallel()
    #             for child in headPieces.getChildren():
    #                 x, y, z = child.getPos()
    #                 vec = numpy.array([x, y + 3 * (-1 if y_0 > 0 else 1), z_0 + 5])
    #                 x_pos, y_pos, z_pos = numpy.array([x_0, y_0, -5]) + vec * 60 / numpy.linalg.norm(vec)
    #                 para.append(LerpPosInterval(child, duration=0.8, pos=(x_pos, y_pos, z_pos)))
    #
    #             self.seqHolder[-1].append(Sequence(Func(seqNode.play, 0, 17), Wait(17 / 24),
    #                                                Func(texCard.removeNode), Func(keeper.btn.np.removeNode),
    #                                                Func(headPieces.setPos, x_0, y_0, z_0), para)
    #                                       )
    #
    # def minionsDieAni(self, entities):
    #     para = Parallel()
    #     for keeper in entities:
    #         if keeper.btn: para.append(Func(keeper.btn.dimDown))
    #     self.seqHolder[-1].append(para)
    #     self.seqHolder[-1].append(Wait(0.3))
    #
    # def deathrattleAni(self, keeper):
    #     if keeper.btn:
    #         x, y, z = keeper.btn.np.getPos()
    #         texCard, seqNode = makeTexCard(self, "TexCards\\Shared\\Deathrattle.egg", pos=(x, y + 0.4, z + 0.3), scale=3.3)
    #         self.seqHolder[-1].append(Sequence(Func(seqNode.play), Wait(1.2), Func(texCard.removeNode)))
    #
    # def weaponPlayedAni(self, card):
    #     ID = card.ID
    #     handZone = self.handZones[ID]
    #     x, y, z = self.heroZones[ID].weaponPos
    #     card.btn.isPlayed = True  # The minion must be first set to isPlayed=True, so that the later statChangeAni can correctly respond
    #     sequence = Sequence(LerpPosHprScaleInterval(card.btn.np, duration=0.25, pos=(x, y + 0.2, z + 5), hpr=(0, 0, 0), scale=1),
    #                         Func(card.btn.changeCard, card, True),
    #                         Parallel(handZone.placeCards(False), LerpPosInterval(card.btn.np, duration=0.25, pos=(x, y, z)))
    #                         )
    #     self.seqHolder[-1].append(sequence)
    #
    # def secretTrigAni(self, card): #Secret trigger twice will show the animation twice.
    #     if not (nodepath := card.btn.np): seq = Sequence()
    #     else: seq = Sequence(Func(self.offsetNodePath_Wait, nodepath, duration=0.15, dx=0.1, add2Queue=False),
    #                          Func(self.offsetNodePath_Wait, nodepath, duration=0.15, dx=-0.2, add2Queue=False),
    #                          Func(self.offsetNodePath_Wait, nodepath, duration=0.15, dx=0.1, add2Queue=False),
    #                          Wait(0.3), Func(nodepath.removeNode)
    #                          )
    #     scale_Max, scale_Min = (25, 1, 25 * 600 / 800), (1, 1, 1 * 600 / 800)
    #     texCard = self.forGameTex["Secret%s" % card.Class]
    #     seq.append(LerpPosHprScaleInterval(texCard, duration=0.3, pos=(0, 1, 9), hpr=(0, -90, 0), scale=scale_Max))
    #     seq.append(Wait(0.8))
    #     seq.append(LerpPosHprScaleInterval(texCard, duration=0.3, pos=(0, 0, 0), hpr=(0, -90, 0), scale=scale_Min))
    #     self.seqHolder[-1].append(seq)
    #     self.showOffBoardTrig(card)
    #     self.heroZones[card.ID].placeSecrets()
    #
    # def need2Hide(self, card):  # options don't have ID, so they are always hidden if the PvP doesn't show enemy hand
    #     return not self.showEnemyHand and self.sock_Send and (not hasattr(card, "ID") or card.ID != self.ID)
    #
    # def showOffBoardTrig(self, card, animationType="Curve", text2Show='', textY=-3, isSecret=False):
    #     # tprint("showOffBoardTrig ",card)
    #     #召唤时出现了
    #     if card:
    #         y = self.heroZones[card.ID].heroPos[1]
    #         # if card.btn and isinstance(card.btn, Btn_Card) and card.btn.np: nodePath, btn_Card = card.btn.np, card.btn
    #         nodePath, btn_Card = self.addCard(card, pos=(0, 0, 0), pickable=False, isUnknownSecret=isSecret and self.need2Hide(card))
    #         if text2Show:
    #             textNode = TextNode("Text Disp")
    #             textNode.setText(text2Show)
    #             textNode.setAlign(TextNode.ACenter)
    #             textNodePath = nodePath.attachNewNode(textNode)
    #             textNodePath.setPosHpr(0, textY, 1, 0, -90, 0)
    #         seq = self.seqHolder[-1] if self.seqHolder else Sequence()
    #         if animationType == "Curve":
    #             moPath = Mopath.Mopath()
    #             moPath.loadFile("Models\\BoardModels\\DisplayCurve_%s.egg" % ("Lower" if y < 0 else "Upper"))
    #             seq.append(MopathInterval(moPath, nodePath, duration=0.3))
    #             seq.append(Wait(1))
    #         elif animationType == "Appear":
    #             pos = pos_OffBoardTrig_1 if y < 0 else pos_OffBoardTrig_2
    #             seq.append(Func(nodePath.setPos, pos[0], pos[1], 0))
    #             seq.append(LerpPosHprScaleInterval(nodePath, duration=0.4, pos=pos, hpr=(0, 0, 0), startScale=0.3, scale=1))
    #             seq.append(Wait(0.7))
    #             seq.append(LerpScaleInterval(nodePath, duration=0.2, scale=0.2))
    #         else:  # typically should be ''
    #             seq.append(Func(nodePath.setPos, pos_OffBoardTrig_1 if y < 0 else pos_OffBoardTrig_2))
    #             seq.append(Wait(1))
    #         seq.append(Func(nodePath.removeNode))
    #         if not self.seqHolder: seq.start()
    #
    # #显示大卡图
    # def addCard(self, card, pos, pickable, isUnknownSecret=False, onlyShowCardBack=False, isPlayed=False):
    #     TEMP_MSG("showCard ", card.__class__.__name__)
    #     if card.category == "Option":
    #         nodePath, btn_Card = genOption(self, card, pos=pos, onlyShowCardBack=onlyShowCardBack)  # Option cards are always pickable
    #     else:
    #         btn_Orig = card.btn if card.btn and card.btn.np else None
    #         nodePath, btn_Card = genCard(self, card, pos=pos, isPlayed=isPlayed, pickable=pickable,
    #                                      onlyShowCardBack=onlyShowCardBack, makeNewRegardless=True, isUnknownSecret=isUnknownSecret)
    #         if btn_Orig: card.btn = btn_Orig  # 一张牌只允许存有其创建伊始指定的btn，不能在有一个btn的情况下再新加其他的btn
    #     return nodePath, btn_Card
    #
    # # Targeting/AOE animations
    # def targetingEffectAni(self, subject, target):
    #     return
    #
    # # Miscellaneous animations
    # def turnEndButtonAni_FlipRegardless(self):
    #     interval = self.btnTurnEnd.np.hprInterval(0.4, (0, 180 - self.btnTurnEnd.np.get_p(), 0))
    #     self.seqHolder[-1].append(Func(self.btnTurnEnd.changeDisplay, False))
    #     self.seqHolder[-1].append(Func(interval.start))
    #
    # def turnEndButtonAni_Flip2RightPitch(self):
    #     p = 0 if self.ID == self.Game.turn else 180
    #     if self.btnTurnEnd.np.get_p() != p:
    #         interval = self.btnTurnEnd.np.hprInterval(0.4, (0, p, 0))
    #         self.seqHolder[-1].append(Func(interval.start))
    #
    # def turnStartAni(self):
    #     self.turnEndButtonAni_Flip2RightPitch()
    #     if self.ID != self.Game.turn: return
    #     #tex_Parts = self.forGameTex["TurnStart_Particles"]
    #     #tex_Banner = self.forGameTex["TurnStart_Banner"]
    #     #seqNode_Parts = tex_Parts.find("+SequenceNode").node()
    #     #seqNode_Banner = tex_Banner.find("+SequenceNode").node()
    #     #seqNode_Parts.pose(0)
    #     #seqNode_Banner.pose(0)
    #     #sequence_Particles = Sequence(Func(tex_Parts.setPos, 0, 1, 5), Func(seqNode_Parts.play, 0, 27), Wait(0.9),
    #     #							  Func(tex_Parts.setPos, 0, 0, 0))  # #27 returns to the begin
    #     #sequence_Banner = Sequence(
    #     #	LerpPosHprScaleInterval(tex_Banner, duration=0.2, pos=(0, 1, 6), hpr=(0, -90, 0), startScale=1,
    #     #							scale=(23, 1, 23 * 332 / 768)),
    #     #	Func(seqNode_Banner.play), Wait(1.2),
    #     #	LerpPosHprScaleInterval(tex_Banner, duration=0.2, pos=(0, 0, 0), hpr=(0, 0, 0), scale=(0.15, 0.15, 0.15))
    #     #	)
    #     #self.seqHolder[-1].append(Parallel(sequence_Particles, sequence_Banner))
    #     self.seqHolder[-1].append(Sequence(LerpPosHprScaleInterval(self.np_YourTurnBanner, duration=0.3, pos=(0, 0, 4), hpr=(0, 0, 0), startScale=0.3, scale=1),
    #                                        Wait(0.7),
    #                                        LerpPosHprScaleInterval(self.np_YourTurnBanner, duration=0.3, pos=(0, 0, 0), hpr=(0, 0, 0), scale=0.3))
    #                               )


    def turnStartAni(self,ID):
        for ID,avatar in self.avatars.items():
            avatar.playanimTurnStart(ID)
    #
    # def usePowerAni(self, card):
    #     x, y, z = self.heroZones[card.ID].powerPos
    #     np = card.btn.np
    #     sequence = Sequence(LerpPosHprInterval(np, duration=0.2, pos=(x, y, z + 3), hpr=Point3(0, 0, 90)),
    #                         LerpPosHprInterval(np, duration=0.2, pos=(x, y, z), hpr=Point3(0, 0, 180)))
    #     if card.ID == self.Game.turn and not card.chancesUsedUp():
    #         sequence.append(LerpPosHprInterval(np, duration=0.17, pos=(x, y, z + 3), hpr=(0, 0, 90)))
    #         sequence.append(LerpPosHprInterval(np, duration=0.17, pos=(x, y, z), hpr=(0, 0, 0)))
    #     self.seqHolder[-1].append(Func(sequence.start))
    #
    # """Mouse click setup"""
    # #The camera carries a CollisionNode that has a solid collision volume. Its nodepath is added to the CollisionTraverser.
    # #When invoked, CollisionTraverser checks for collision added (Only between Collision Ray and other volumes)
    # def init_CollisionSetup(self):
    #     self.cTrav, self.collHandler, self.raySolid = CollisionTraverser(), CollisionHandlerQueue(), CollisionRay()
    #     (cNode := CollisionNode("cNode")).addSolid(self.raySolid)
    #     (cNodePath_Picker := self.camera.attachNewNode(cNode))#.show()
    #     self.cTrav.addCollider(cNodePath_Picker, self.collHandler)
    #     self.raySolid.setOrigin(0, 0, CamPos_Z)
    #
    # def setRaySolidDirection(self):
    #     mpos = self.mouseWatcherNode.getMouse()
    #     #self.crosshair.show()
    #     # Reset the Collision Ray orientation, based on the mouse position
    #     self.raySolid.setDirection(24 * mpos.getX(), 13.3 * mpos.getY(), -50.5)
    #
    # def mouse1_Down(self):
    #     if self.mouseWatcherNode.hasMouse():
    #         self.setRaySolidDirection()
    #
    # def mouse1_Up(self):
    #     if self.mouseWatcherNode.hasMouse():
    #         self.setRaySolidDirection()
    #         if self.collHandler.getNumEntries() > 0:
    #             self.collHandler.sortEntries()
    #             #Scene graph tree is written in C. To store/read python objects, use NodePath.setPythonTag/getPythonTag('attrName')
    #             if btn := self.collHandler.getEntry(0).getIntoNodePath().getParent().getPythonTag("btn"):
    #             btn.leftClick()
    #
    # def mouse3_Down(self):
    #     if self.mouseWatcherNode.hasMouse():
    #         self.setRaySolidDirection()
    #
    # def mouse3_Up(self):
    #     if self.mouseWatcherNode.hasMouse():
    #         self.setRaySolidDirection()
    #         if self.collHandler.getNumEntries() > 0:
    #             self.collHandler.sortEntries()
    #             cNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
    #             if self.stage != 0: self.cancelSelection()
    #             elif btn := cNode_Picked.getParent().getPythonTag("btn"):
    #             btn.rightClick()
    #     else: self.cancelSelection()
    #
    # def clearDrawnCards(self):
    #     self.playedCards = []
    #     for child in self.render.getChildren():
    #         if not (child.name.startswith("Model2Keep")
    #                 or child.name.startswith("Tex2Keep")
    #                 or child.name.startswith("Text2Keep")):
    #             print("Remove", child.name, type(child))
    #             child.removeNode()
    #     for child in self.render.getChildren():
    #         if "2Keep" not in child.name:
    #             print("Kept under render (those that shouldn't):", child.name, type(child))
    #     print(self.cam.getPos(), self.cam.getHpr(), self.camLens.getFov())
    #     self.arrow.hide()
    #     self.deckZones = {}
    #
    # #ui使用
    # def mainTaskLoop(self, task):
    #     # seqReady默认是True，只在游戏结算和准备动画过程中把seqReady设为False，保证尚未完成的seq不被误读
    #     # 完成sequence的准备工作时会把seqReady再次设为True
    #     # 只有把当前正在进行的seq走完之后才会读取下一个seq
    #     if self.seqReady and self.seqHolder and not (self.seq2Play and self.seq2Play.isPlaying()):
    #         self.seq2Play = self.seqHolder.pop(0)
    #         self.seq2Play.append(Func(self.decideCardColors))
    #         self.seq2Play.start()
    #     # tkinter window必须在主线程中运行，所以必须在ShowBase的main loop中被执行
    #     # self.msg_Exit随时可以被设为非空值。但是一定要等到GUI中的所有seq都排空并且没有正在播放的seq了之后才会退出当前游戏
    #     # 实际上就是只有当GUI处于空闲状态时才会执行
    #     elif self.msg_Exit and self.seqReady and not self.seqHolder and not (self.seq2Play and self.seq2Play.isPlaying()):
    #         # print("\n\n----------\nCheck restart layer 1 window:", self.msg_Exit, self.seqReady, self.seqHolder, self.seq2Play, self.seq2Play and self.seq2Play.isPlaying())
    #         self.seqReady, self.seq2Play, self.msg_Exit = True, None, ''
    #         self.clearDrawnCards()
    #         self.deckBuilder.root.unstash()
    #         return Task.cont
    #
    #     if self.mouseWatcherNode.hasMouse(): #如果鼠标在窗口内
    #         self.setRaySolidDirection() #不断地把RaySolid重置
    #         #只要self.arrow和self.crosshair有一个正在显示，就取消卡牌的放大
    #         if not (self.arrow.isHidden() and self.crosshair.isHidden()):
    #             self.stopCardZoomIn()
    #             self.replotArrowCrosshair()
    #         elif self.btnBeingDragged: #如果有被拖动的卡牌，则取消卡牌的放大
    #             self.stopCardZoomIn()
    #             self.dragCard() #拖动卡牌
    #         #如果RaySolid有碰撞发生
    #         elif self.collHandler.getNumEntries() > 0:
    #             self.collHandler.sortEntries()
    #             cNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
    #             btn_Picked = cNode_Picked.getParent().getPythonTag("btn")
    #             #在组建套牌期间，只要鼠标移到了套牌中卡牌之外的地方就会取消。卡牌收藏区域的卡牌不设置放大功能
    #             if self.stage < 0:
    #                 if isinstance(btn_Picked, Btn_CardinDeck): self.drawCardZoomIn(btn_Picked)
    #                 else: self.stopCardZoomIn()
    #             else: #游戏过程中，指向了一个对应手牌的btn时才会响应。drawCardZoomIn自行判断指着的这张牌是否已经放大
    #                 if hasattr(btn_Picked, "card") and btn_Picked.card and hasattr(btn_Picked.card, "inHand") \
    #                         and btn_Picked.card.inHand and abs(btn_Picked.np.getY()) > 11.5: #如果手牌中的牌远离手牌区域，则不进行显示
    #                     self.drawCardZoomIn(btn_Picked)
    #         #RaySolid没有碰撞时，如果此时不是游戏中或者有一个手牌在被放大，则取消放大
    #         #实际上很少会有需要调用此处的需要，因为背景也有较大的碰撞体积，所以在部分时候都会有RaySolid的碰撞
    #         elif self.np_CardZoomIn and (self.stage < 0 or self.np_CardZoomIn.getPythonTag("btn").card.inHand):
    #             self.stopCardZoomIn()
    #     return Task.cont
    #
    # def drawCardZoomIn(self, btn):
    #     # Stop showing for btns without card and hero and cards not allowed to show to enemy(hand and secret).
    #     if self.stage == -2:  # 在组建套牌时调用这个函数时一定是要放大一张牌
    #         card, drawNew = btn.cardEntity, True
    #         if self.np_CardZoomIn:  # 如果当前有放大的卡牌且不是指向的卡牌时，重新画一个；如果是相同的卡牌则无事发生
    #             if card != self.np_CardZoomIn.getPythonTag("btn").card:
    #                 self.np_CardZoomIn.removeNode()
    #             else: drawNew = False  # 只有目前有放大卡牌且就是指向的卡牌时，才不会重新画一个
    #         if drawNew:
    #             x, y, z = btn.np.getPos()
    #             self.np_CardZoomIn = self.addCard(card, pos=(x-10, 0.75*y, z+3), pickable=False)[0]
    #             self.np_CardZoomIn.setScale(2)
    #     # 在游戏过程中放大一张牌时
    #     elif self.stage > -1:
    #         card = btn.card
    #         # 想要放大场上的英雄，或者一个对方手牌中应该只显示了卡背的牌时会失败，并取消当前的放大。
    #         if (card.category == "Hero" and card is self.Game.heroes[card.ID]) or \
    #                 (card.inHand and btn.onlyCardBackShown):
    #             self.stopCardZoomIn()
    #         else:  # 在游戏中放大一张牌的时候需要判断其是否是一张要隐瞒的奥秘，并显示一张牌的扳机和附魔效果
    #             if self.np_CardZoomIn and self.np_CardZoomIn.getPythonTag("btn").card == card:
    #                 return  # 如果正在放大的牌就是当前指着的牌的话，则直接返回
    #             if self.np_CardZoomIn: self.np_CardZoomIn.removeNode()
    #             # 手牌中的牌放大时在其上下方；而其他卡牌的放大会在屏幕左侧显示
    #             pos = (btn.np.getX() if hasattr(card, "inHand") and card.inHand else ZoomInCard_X,
    #                    ZoomInCard1_Y if self.ID == card.ID else ZoomInCard2_Y, ZoomInCard_Z)
    #             #需要隐瞒的奥秘需要在卡面上盖未知奥秘的卡图；只有场上英雄在放大时是不显示完整卡图
    #             self.np_CardZoomIn, btn = self.addCard(card, pos, pickable=False,
    #                                                    isUnknownSecret=card.race == "Secret" and self.need2Hide(card),
    #                                                    isPlayed=card.category == "Hero" and card.onBoard)
    #             if btn: btn.effectChangeAni()
    #             # Display the creator of the card at the bottom
    #             if card.creator:
    #                 genHeroZoneTrigIcon(self, card.creator(self.Game, card.ID), pos=(-1.4, -4.88, 0),
    #                                     scale=1)[0].reparentTo(self.np_CardZoomIn)
    #                 valueText = self.txt("Created by:\n") + card.creator.name_CN if self.lang == "CN" else card.creator.name
    #                 makeText(self.np_CardZoomIn, "Text", valueText=valueText, pos=(-0.8, -4.7, 0),
    #                          scale=0.45, color=white, font=self.getFont(self.lang))[1].setAlign(TextNode.ALeft)
    #             # Add the tray of enchantments onto the card
    #             i = 0
    #             for enchant in card.enchantments:
    #                 self.showEnchantTrigDeath(enchant.source, enchant.text(), i)
    #                 i += 1
    #             for trig in card.trigsBoard + card.trigsHand + card.deathrattles:
    #                 if not trig.inherent:
    #                     typeTrig = type(trig)
    #                     name = typeTrig.cardType.name_CN if self.lang == "CN" else typeTrig.cardType.name
    #                     self.showEnchantTrigDeath(typeTrig.cardType, name+"\n"+typeTrig.description, i)
    #                     i += 1
    #
    # def showEnchantTrigDeath(self, creator, text, i):
    #     nodepath = genHeroZoneTrigIcon(self, creator(self.Game, 1), pos=(3.15, -i, 0.1), scale=0.9)[0]
    #     nodepath.reparentTo(self.np_CardZoomIn)
    #     makeText(self.np_CardZoomIn, "Text", valueText=text, pos=(3.7, -i + 0.06, 0.1), scale=0.3,
    #              color=black, font=self.getFont(self.lang), wordWrap=20, cardColor=yellow)[1].setAlign(TextNode.ALeft)
    #
    # def stopCardZoomIn(self):
    #     if self.np_CardZoomIn:
    #         self.np_CardZoomIn.removeNode()
    #         self.np_CardZoomIn = None
    #
    # def calcMousePos(self, z):
    #     vec_X, vec_Y, vec_Z = self.raySolid.getDirection()
    #     delta_Z = abs(CamPos_Z - z)
    #     x, y = vec_X * delta_Z / (-vec_Z), vec_Y * delta_Z / (-vec_Z)
    #     return x, y
    #
    # def dragCard(self):
    #     if self.btnBeingDragged.cNode:
    #         self.btnBeingDragged.cNode.removeNode()  # The collision nodes are kept by the cards.
    #         self.btnBeingDragged.cNode = None
    #
    #     # Decide the new position of the btn being dragged
    #     z = self.btnBeingDragged.np.getZ()
    #     x, y = self.calcMousePos(z)
    #     self.btnBeingDragged.np.setPosHpr(x, y, z, 0, 0, 0)
    #     # No need to change the x, y, z of the card being dragged(Will return anyway)
    #     card = self.btnBeingDragged.card
    #     if card.category == "Minion":
    #         minionZone = self.minionZones[card.ID]
    #         ownMinions = self.Game.minions[card.ID]
    #         boardSize = len(ownMinions)
    #         if not ownMinions: self.pos = -1
    #         elif len(ownMinions) < 7:
    #             ls_np_temp = [minion.btn.np for minion in ownMinions]
    #             posMinions_Orig = posMinionsTable[minionZone.y][boardSize]
    #             posMinions_Plus1 = posMinionsTable[minionZone.y][boardSize + 1]
    #             if -6 > y or y > 6:  # Minion away from the center board, the minions won't shift
    #                 dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Orig[i] for i in range(boardSize)}
    #                 self.pos = -1
    #             elif minionZone.y - 3.8 < y < minionZone.y + 3.8:
    #                 # Recalculate the positions and rearrange the minion btns
    #                 if x < ls_np_temp[0].get_x():  # If placed leftmost, all current minion shift right
    #                     dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Plus1[i + 1] for i in range(boardSize)}
    #                     self.pos = 0
    #                 elif x < ls_np_temp[-1].get_x():
    #                     ind = next((i + 1 for i, nodePath in enumerate(ls_np_temp[:-1]) if nodePath.get_x() < x < ls_np_temp[i+1].get_x()), -1)
    #                     if ind > -1:
    #                         dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Plus1[i + (i >= ind)] for i in range(boardSize)}
    #                         self.pos = ind
    #                     else: return  # If failed to find
    #                 else:  # All minions shift left
    #                     dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Plus1[i] for i in range(boardSize)}
    #                     self.pos = -1
    #             else:  # The minion is dragged to the opponent's board, all minions shift left
    #                 dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Plus1[i] for i in range(boardSize)}
    #                 self.pos = -1
    #             for nodePath, pos in dict_MinionNp_Pos.items(): nodePath.setPos(pos)
    #
    # def stopDraggingCard(self, returnDraggedCard=True):
    #     btn = self.btnBeingDragged
    #     if btn:
    #         btn.cNode = btn.np.attachNewNode(btn.cNode_Backup)
    #         self.btnBeingDragged = None
    #         if not returnDraggedCard:
    #             self.playedCards.append(self.subject)
    #             return
    #         ID = btn.card.ID
    #         # Put the card back in the right pos_hpr in hand
    #         handZone_Y, ownHand = self.handZones[ID].y, self.Game.Hand_Deck.hands[ID]
    #         if btn.card in ownHand:
    #             i = ownHand.index(btn.card)
    #             pos, hpr = posHandsTable[handZone_Y][len(ownHand)][i], hprHandsTable[handZone_Y][len(ownHand)][i]
    #             btn.np.setPosHpr(pos, hpr)
    #         # Put the minions back to right positions on board
    #         ownMinions = self.Game.minions[ID]
    #         posMinions = posMinionsTable[self.minionZones[ID].y][len(ownMinions)]
    #         for i, minion in enumerate(ownMinions):
    #             minion.btn.np.setPos(posMinions[i])
    #
    # def replotArrowCrosshair(self):
    #     # Decide the new orientation and scale of the arrow
    #     if self.subject and self.subject.btn and self.subject.btn.np:
    #         x_0, y_0, z_0 = self.subject.btn.np.getPos()
    #     else: x_0, y_0, z_0 = 0, 0, 1.4
    #     x, y = self.calcMousePos(z_0)
    #     if not self.arrow.isHidden():
    #         degree, distance = self.getDegreeDistance_fromCoors(x_0, y_0, x, y)
    #         self.arrow.setPosHprScale(x_0, y_0, z_0, degree, 0, 0, 1, distance / 7.75, 1)
    #     if not self.crosshair.isHidden():
    #         self.crosshair.setPos(x, y, 1.4)
    #
    # """Game resolution setup"""
    def cancelSelection(self, returnDraggedCard=True, keepSubject=False, keepTarget=False, keepChoice=False, keepPos=False):
        return
        # self.stopDraggingCard(returnDraggedCard)
        # self.arrow.hide()
        #
        # if 3 > self.stage > -1:  # 只有非发现状态,且游戏不在结算过程中时下才能取消选择
        #     if self.subject:
        #         for option in self.subject.options:
        #             if option.btn:
        #                 if option.btn.np: option.btn.np.removeNode()
        #                 option.btn = None
        #     for card in self.target: #self.target can be empty
        #         if card.btn and card.btn.np and (np := card.btn.np.find("ithTarget_TextNode")):
        #             np.removeNode()
        #     subject, target, choice, pos = self.subject, self.target, self.choice, self.pos
        #     self.subject, self.target = None, []
        #     self.stage, self.step, self.pos, self.choice = 0, "", -1, -1
        #     self.resetCardColors()
        #
        #     curTurn = self.Game.turn
        #     for card in self.Game.Hand_Deck.hands[curTurn] + self.Game.minions[curTurn] \
        #                 + [self.Game.heroes[curTurn], self.Game.powers[curTurn]]:
        #         if card.btn and not (card.inHand and card.btn.onlyCardBackShown): card.btn.setBoxColor(
        #             card.btn.decideColor())
        #
        #     for card in self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2] + [self.Game.powers[1]] + [
        #         self.Game.powers[2]]:
        #         if hasattr(card, "targets"): card.targets = []
        #
        #     if keepSubject: self.subject = subject
        #     if keepTarget: self.target = target
        #     if keepChoice: self.choice = choice
        #     if keepPos: self.pos = pos
    #
    # #专门用于卡牌效果的目标选取。对于所有需要的序号判断是否有合法目标。如果某个序号没有合法目标，则当前的目标为None，跳到下一个选择。
    # #如果剩余的选择中有合法目标，则返回2
    # #如果剩余的所有选择中均没有合法目标的话，但之前已经有选择了的目标，则返回1；如果所有的序号都没有合法目标，则返回0
    # def findTargetsandHighlight(self):
    #     target = ()
    #     for ith in range(len(self.target), self.subject.numTargetsNeeded(self.choice)):
    #         if target := self.subject.findTargets(self.choice, ith, exclude=self.target):
    #         break
    #     else: self.target.append(None)
    # if target: #剩余的选择中有合法目标。可以高亮合法目标，并显示箭头。
    #     self.highlightTargets(target)
    #     self.arrow.show()
    #     self.arrow.setPos(self.subject.btn.np.getPos())
    #     return 2
    # else: return 0 + any(obj for obj in self.target) #如果已选的目标中的合法目标，则返回1，否则返回0
    #
    #
    #
    # #能够被选择的目标必须是目前不在卡池里面的，是可以被效果选择到的，且是效果的合法目标。
    # #是合法目标的前提下，向self.target中添加。如果卡牌效果得到了所有需要的目标，则返回True，然后开始打出操作。
    # def isLegalTarget_canFinishSelection(self, card):
    #     if card not in self.target and self.subject.canSelect(card) \
    #             and self.subject.targetCorrect(card, self.choice, ith=len(self.target)):
    #         self.target.append(card)
    #         if len(self.target) >= self.subject.numTargetsNeeded(self.choice): return True
    #         else: #需要给被选择的卡牌标其现在是第几号被选择的目标。
    #             makeText(card.btn.np, "ithTarget", str(len(self.target)), pos=(0, 0, 1), scale=1.5, color=red, font=self.getFont())
    #             return self.findTargetsandHighlight() < 2
    #     return False
    #
    # def checkifStartChooseOne(self, card):
    #     if card.options and self.Game.rules[card.ID]["Choose Both"] < 1:
    #         self.stage = 1
    #         leftMost_X = -5 * (len(card.options) - 1) / 2
    #         for i, option in enumerate(card.options):
    #             available = option.available()
    #             nodePath, _ = self.addCard(option, pos=(leftMost_X + i * 5, 1.5, 10), pickable=available)
    #             if not available: nodePath.setColor(grey)
    #         return True
    #     else:
    #         self.choice = -1
    #         return False
    #
    # def selectedPowerasSubject(self, card, button):
    #     # 英雄技能会自己判定是否可以使用。
    #     if card.numTargetsNeeded(self.choice):  # selectedSubject之前是"Hero Power 1"或者"Hero Power 2"
    #         self.step = "Power"
    #         self.findTargetsandHighlight()
    #     else:
    #         self.cancelSelection(keepSubject=True, keepChoice=True)
    #         self.gamePlayQueue.append(lambda: self.Game.usePower(self.subject, (), self.choice))
    #
    # # Can only be invoked by the game thread
    # def waitforDiscover(self):
    #     self.stage, self.discover = 3, None
    #     para = Parallel()
    #     btns = []
    #     leftMost_x = -5 * (len(self.Game.options) - 1) / 2
    #     for i, card in enumerate(self.Game.options):
    #         # self.addCard creates a btn for the card, but the card's original button(if any) is kept.
    #         # There will be two btns referencing the same card
    #         nodePath_New, btn_New = self.addCard(card, Point3(0, 0, 0), pickable=True)
    #         btns.append(btn_New)
    #         para.append(LerpPosHprScaleInterval(nodePath_New, duration=0.2, pos=(leftMost_x + 5 * i, 1.5, 13),
    #                                             hpr=(0, 0, 0), startScale=0.2, scale=1))
    #     self.seqHolder[-1].append(para)
    #     btn_HideOptions = DirectButton(text=("Hide", "Hide", "Hide", "Continue"), scale=.1,
    #                                    pos=(2, 0, 2), command=self.toggleDiscoverHide)
    #     btn_HideOptions["extraArgs"] = [btn_HideOptions]
    #     self.btns2Remove.append(btn_HideOptions)
    #     self.seqHolder[-1].append(Func(btn_HideOptions.setPos, -0.5, 0, -0.5))
    #     self.seqReady = True
    #     while self.discover is None:
    #         time.sleep(0.1)
    #     self.stage = 0
    #     # Restart the sequence
    #     self.seqReady = False
    #     self.seqHolder.append(Sequence())
    #     for btn in btns: btn.np.detachNode()
    #     for btn in self.btns2Remove: btn.destroy()
    #     return self.discover  # No need to reset the self.discover. Need to reset each time anyways
    #
    # def toggleDiscoverHide(self, btn):
    #     print("Toggle hide button", btn["text"])
    #     if btn["text"] == ("Hide", "Hide", "Hide", "Continue"):
    #         btn["text"] = ("Show", "Show", "Show", "Continue")
    #         for card in self.Game.options: card.btn.np.hide()
    #     else:  # btn["text"] == ("Show", "Show", "Show", "Continue")
    #         btn["text"] = ("Hide", "Hide", "Hide", "Continue")
    #         for card in self.Game.options: card.btn.np.show()
    #
    # # To be invoked for animation of opponent's discover decision (if PvP) or own random decisions
    # def discoverDecideAni(self, isRandom, indPick, options):
    #     seq, para = self.seqHolder[-1], Parallel()
    #     btn_Chosen, btns = None, []
    #     leftMost_x = -5 * (len(options) - 1) / 2
    #     if isinstance(options, (list, tuple)):
    #         for i, card in enumerate(options):
    #             nodePath, btn = self.addCard(card, Point3(0, 0, 0), pickable=True,
    #                                          onlyShowCardBack=self.need2Hide(card))
    #             btns.append(btn)
    #             if i == indPick: btn_Chosen = btn
    #             para.append(LerpPosHprScaleInterval(nodePath, duration=0.2, pos=(leftMost_x + 5 * i, 1.5, 13),
    #                                                 hpr=(0, 0, 0), startScale=0.2, scale=1))
    #     seq.append(para)
    #     seq.append(Wait(0.5) if isRandom else Wait(1.2))
    #     sequence = Sequence(LerpScaleInterval(btn_Chosen.np, duration=0.2, scale=1.13),
    #                         LerpScaleInterval(btn_Chosen.np, duration=0.2, scale=1.0))
    #     for btn in btns: sequence.append(Func(btn.np.detachNode))  # The card might need to be added to hand
    #     seq.append(sequence)
    #
    # # For choosing a target onBoard during effect resolution
    # def waitforChoose(self, ls):
    #     self.stage, self.discover = 3, None
    #     self.seqHolder[-1].append(Func(self.highlightTargets, ls))
    #     self.seqReady = True
    #     self.crosshair.show()
    #
    #     while self.discover not in ls:
    #         time.sleep(0.1)
    #     self.stage = 0
    #     # Restart the sequence
    #     self.crosshair.hide()
    #     self.resetCardColors()
    #     self.seqReady = False
    #     self.seqHolder.append(Sequence())
    #     return self.discover  # No need to reset the self.discover. Need to reset each time anyways
    #
    # # options should be real card objs
    # def chooseDecideAni(self, isRandom, indexOption, options):
    #     nodePath = (option := options[indexOption]).btn.np
    #     seq = Sequence(Func(self.highlightTargets, options), Func(self.crosshair.setPos, 0, 0, 1.4),
    #                    # The crosshair wrtReparentTo the target it will point to, then moves onto it, then reparentTo render
    #                    Func(self.crosshair.wrtReparentTo, nodePath), Func(self.crosshair.show),
    #                    LerpPosInterval(self.crosshair, duration=0.2 if isRandom else 0.5, pos=(0, 0.5, 0.3)),
    #                    Wait(0.4), Func(self.crosshair.hide), Func(self.crosshair.reparentTo, self.render),
    #                    Func(self.resetCardColors)
    #                    )
    #     self.seqHolder[-1].append(seq)
    #
    # def checkCardsDisplays(self, side=0, checkHand=False, checkBoard=False):
    #     sides = (side,) if side else (1, 2)
    #     if checkHand:
    #         print("   Check cards in hands:")
    #         for ID in sides:
    #             for card in self.Game.Hand_Deck.hands[ID]:
    #                 if not card.btn.np.getParent():
    #                     print("	  ", ID, card.name, card.btn.np, card.btn.np.getParent(), card.btn.np.getPos())
    #     if checkBoard:
    #         print("   Check cards on Board:")
    #         for ID in sides:
    #             for card in self.Game.minions[ID]:
    #                 if not card.btn.np.getParent():
    #                     print("	  ", ID, card.name, card.btn.np, card.btn.np.getParent(), card.btn.np.getPos())
    #
    # def sendOwnMovethruServer(self, endingTurn=True):
    #     pass
    #
    # def back2Layer1(self, btn=None):
    #     self.stage = -2
    #     self.msg_Exit = "Go Back to Layer 1"
    #     self.seqReady = True