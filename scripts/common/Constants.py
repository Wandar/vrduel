 # -*- coding: utf-8 -*-
class MyEnum:
    def __new__(cls, *args, **kwargs):
        import KBEDebug
        KBEDebug.ERROR_MSG("new Enum is forbidden")
        return

class BidreDict(MyEnum):
    __bidre__ = True
    pass


GAME_VERSION="0.1.1" #no use,to prevent client from logining,please change script_version in kbengineOrigin.xml


#"error"
FAIL = 1
SUCCESS = 0
ERR_ROOM_FULL = 1
ERR_ROOM_NOT_EXIST = 2
ERR_HASLOCK=3
UNEXPECTED_FAIL=55 #用于except
ERR_REQUEST_TIMEOUT=56
ERR_PRODUCTORMONEY=57


ERR_TIME_OVER=65534


#SPACE
FAIL_DECK_ILLEGAL=2

class CLIENT_TYPE:
    unknow=0
    web=1
    oculus=2
    pico=3
    steamnovr=4
    steamvr=5
    bot=6
    oculuspcvr=7
    android=8
    ios=9


class SPACE_TYPE(MyEnum):
    idle=0
    home=1
    tutorial=2
    debug=3
    mpublic=4
    mprivate=5 #暂时没有,public加密码
    matchmaking=6


class SPACE_STATE:
    creating = -1#正在创建类
    initing = 0 #正在初始化
    stored = 1 #没有被使用
    normal = 3 #正在使用,可以加入
    trydestroying=4 #正在尝试销毁


class CONTROLLER(MyEnum):
    none=0
    AButton=1
    AButtonDown=2
    BButton=3
    BButtonDown=4
    XButton=5
    XButtonDown=6
    YButton=7
    YButtonDown=8
    LeftTrigger=9
    LeftTriggerDown=10
    LeftGrip=11
    LeftGripDown=12
    LeftThumbstick=13
    LeftThumbstickDown=14
    RightTrigger=15
    RightTriggerDown=16
    RightGrip=17
    RightGripDown=18
    RightThumbstick=19
    RightThumbstickDown=20
    StartButton=21
    StartButtonDown=22
    BackButton=23
    BackButtonDown=24


SERVER_SUCCESS=0
SERVER_ERR_SRV_NO_READY=1
SERVER_ERR_SRV_OVERLOAD=2
SERVER_ERR_ILLEGAL_LOGIN=3
SERVER_ERR_NAME_PASSWORD=4
SERVER_ERR_NAME=5
SERVER_ERR_PASSWORD=6
SERVER_ERR_ACCOUNT_CREATE_FAILED=7
SERVER_ERR_BUSY=8
SERVER_ERR_ACCOUNT_LOGIN_ANOTHER=9
SERVER_ERR_ACCOUNT_IS_ONLINE=10
SERVER_ERR_PROXY_DESTROYED=11
SERVER_ERR_ENTITYDEFS_NOT_MATCH=12
SERVER_ERR_SERVER_IN_SHUTTINGDOWN=13
SERVER_ERR_NAME_MAIL=14
SERVER_ERR_ACCOUNT_LOCK=15
SERVER_ERR_ACCOUNT_DEADLINE=16
SERVER_ERR_ACCOUNT_NOT_ACTIVATED=17
SERVER_ERR_VERSION_NOT_MATCH=18
SERVER_ERR_OP_FAILED=19
SERVER_ERR_SRV_STARTING=20
SERVER_ERR_ACCOUNT_REGISTER_NOT_AVAILABLE=21
SERVER_ERR_CANNOT_USE_MAIL=22
SERVER_ERR_NOT_FOUND_ACCOUNT=23
SERVER_ERR_DB=24
SERVER_ERR_SPACE_FULL=25
SERVER_ERR_UPDATING=26
SERVER_ERR_LOCAL_PROCESSING=35
SERVER_ERR_ACCOUNT_RESET_PASSWORD_NOT_AVAILABLE=36
SERVER_ERR_ACCOUNT_LOGIN_ANOTHER_SERVER=37


SCENENAME_HelloScene="HelloScene"
SCENENAME_HomeScene="HomeScene"
SCENENAME_IdleScene="IdleScene"
SCENENAME_CITY="cc/city/city"





CB_BASE=1
CB_CELL=0

class EFFECT(MyEnum):
    AA=1
    CC=2


class PANEL_SYNC_TYPE(MyEnum):
    handcard=0
    grave=10#双方的都同步
    banished=20
    bdeck=30


CARD_POS_ISFACE=1 #是否是正面,位
CARD_POS_ISVEL=3

# -2:尚未进入游戏，还在组建套牌，-1:起手调试中，0:游戏中的闲置状态，还未选取任何目标，1:抉择中，2:选择了subject，3:发现选择中
class DUEL_STAGE(MyEnum):
    notingame=-2
    normal=0
    decision=1 #banner
    cardgrabbed=2
    discovering=3

class PHASE(MyEnum):
    prepare=1
    drawing=2
    mainphase1=3
    battle=4
    mainphase2=5
    turnend=6


class COLOR(MyEnum):
    none=0
    yellow=1


LANGUAGE_zh="zh"
LANGUAGE_zh_tr="zh_tr"
LANGUAGE_en="en"


CARDUSE_TYPE_SUMMON=1
CARDUSE_TYPE_CAST=2


class ANIM(MyEnum):
    entityCardReturnToDeck=100
    entityCardReturnToHand=101
    entityCardSendToGY=102
    handcardReturnToDeck=200
    summonMonster=300
    entityAttack=400
    entityUseEffect=500
    playSpell=600


