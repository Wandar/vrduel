# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *


SCENE_J={
    "city/city":{
    }
}


TORNADO_MANAGER_PORT=35687



TO_RADIANS=0.01745329252
TO_DEGREES=57.295779513

ORDER_RELOAD_SCRIPT="reloadScript"
ORDER_RELOAD_DATA="reloadData"
ORDER_RESET="resetServer"
ORDER_GET_NUM='getAccountNum'
ORDER_CLOSING_NOTIFY='closingno'
ORDER_NOTIFY='notify'
ORDER_SAVE_DATA_AND_END='saveDataAndEnd'






class EVENTS:
    dropItem = "dropItem"  #None
    avatarDie = "avatarDie"  #avatar,killer
    avatarEnterRoom = "avatarEnterRoom"  #avatar
    onAvatarClientDeath = "onAvatarClientDeath"
    avatarFall = "avatarFall"

    sendChatToTeammates = "sendChatToTeammates"  #avatar FASTCHAT

    avatarSetHp = "avatarSetHp"  #ava
    avatarChange = "avatarChange"

    avatarKnockSomeone = "avatarKnockSomeone"
    changeScope = "changeScope"  #ava
    changeScopeFocus = "changeScopeFocus"

    #inside
    fall = "fall"
    onHit = "onHit"
    onStopMove = "onStopMove"
    # onCollideObstacle="onCollideObstacle" #entity,depth,collidePos,dir


# class CONTROL_FLAG:
#     doorCollide = int('00000001', 2)
#     die = int('00000010', 2)
#     test = int('00000100', 2)
#     focusSet = int('00001000', 2)
#     fallMove = int('00010000', 2)
#     gameover = int('00100000', 2)
#     kick = int('01000000', 2)
#     punish = int('10000000', 2)


class SERVER_PLAYER_NUM_TYPE:
    empty = 0
    few = 1
    normal = 2
    many = 3
    greatMany = 4
    full = 5


LAYER_COLLIDE = 0

UNLOCK_ERROR = "un0l1ockE2r3rorE49B56f344HjdErK"



CHARGETYPE_IAP = 1
CHARGETYPE_SUBSCRIPTION = 2
CHARGETYPE_CHECKCDK = 9
CHARGETYPE_BECOMEREGULAR = 10
CHARGETYPE_CHANGEPASSWORD = 11



SPACE_DATAS={
    "cc/elveshome/elveshome":{
        "matchingValue":10, #选中作为matchspace的概率
        "duelplacenum":4,
        "maxplayer":20
    },
    "cc/schoolday/schoolday":{
        "matchingValue":10, #选中作为matchspace的概率
        "duelplacenum":4,
        "maxplayer":20
    }
}