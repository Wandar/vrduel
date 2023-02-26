
# -*- coding: utf-8 -*-
import inspect
import random
import tracemalloc
import KBEngine

from globalEventSystem import fire_reloadScript
import util
from mydicts import mySpaces
from util import *


#这个文件存一些控制台常用的简化的方法 from cfunc import *
#只是简化而已,不增加新的功能

#调试功能

def logAllSpaceStats():
    for key,data in mySpaces.items():
        data.logSpaceStats()

#得到gamemanager
def gm():
    return KBEngine.globalData["GameManager"]

#没有用,reload生效之后还是会打印原先的
def logFunc(func):
    util.DEBUG_MSG(inspect.getsourcelines(func))

#重载数据
def rd():
    util.reloadData()

#重载脚本
def rs():
    fire_reloadScript()

#得到所有entity
def les(name=None):
    if util.isBase():
        return KBEngine.entities.items()
    elif util.isCell():
        if name:
            return _lesCell(name)
        else:
            return lesCellAll()

#得到所有avatar的entity
def lesAvatar():
    r={}
    if util.isCell():
        l=KBEngine.entities.items()
        for i,entity in l:
            if entity.className=="Avatar" and not entity.c_isNPC:
                r[entity.id]=entity
    return r

#得到所有entitiy的数量
def lesNum():
    r={}
    for id,en in KBEngine.entities.items():
        n=en.__class__.__name__
        if n not in r:
            r[n]=0
        r[n]+=1
    return r



#show entities by spaceID ,ignore stored simpleObject
def _lesCell(name=None):
    l=KBEngine.entities.items()
    spaces={}
    for i,entity in l:
        if entity.position.x<0:
            pass
        else:
            if entity.spaceID not in spaces:
                spaces[entity.spaceID]=[]
            if (name and entity.__class__.__name__==name) or not name:
                spaces[entity.spaceID].append((i,entity))
    return spaces

def lesCellAll():
    spaces={} #{spaceID:{"obstacle":{"stored":32,"active":44}}}
    for i,en in KBEngine.entities.items():
        spaceIDStr=en.spaceID
        if spaceIDStr not in spaces:
            spaces[spaceIDStr]={}
        name=en.__class__.__name__
        if name not in spaces[spaceIDStr]:
            spaces[spaceIDStr][name]={"stored":0,"active":0}
        if en.position.x<0:
            spaces[spaceIDStr][name]['stored']+=1
        else:
            spaces[spaceIDStr][name]['active']+=1
    return spaces

def gar():
    return KBEngine.entities.garbages.items()
#可能上面的gar调用后en会无法释放
def garKeys():
    return list(KBEngine.entities.garbages.keys())

#显示全部
def less():
    return KBEngine.entities.items()

def ge(idOrName,order=0):
    if isinstance(idOrName,int):
        return KBEngine.entities[idOrName]
    elif isinstance(idOrName,str):
        cnt=0
        for id,en in KBEngine.entities.items():
            getPosFunc=getattr(en,"getPos",None)
            if getPosFunc and getPosFunc()[0]<0:
                continue
            if en.className==idOrName:
                if cnt==order:
                    return en
                cnt+=1


#得到随机一个单位
def feelLucky():
    return random.choice(list(KBEngine.entities.values()))

def reset():
    KBEngine.globalData["Boot"].reset()

def des():
    KBEngine.globalData["Boot"].destroyGameManager()

def resetDebug():
    gm().resetDebugSpace()

def account():
    l=KBEngine.entities.items()
    for i,entity in l:
        if entity.className=="Account":
            return entity

#得到avatar
def avatar():
    l=KBEngine.entities.items()
    if util.isCell():
        for i,entity in l:
            if entity.className=="Avatar" and not entity.c_isNPC:
                return entity
    elif util.isBase():
        for i,entity in l:
            if entity.className=="Avatar":
                return entity

#得到space
def space():
    l=KBEngine.entities.items()
    for i,entity in l:
        if entity.className=="Space":
            return entity

def duel():
    ava=avatar()
    if ava:
        return ava.space.duels[ava.c_duelID]

def game():
    d=duel()
    if d:
        return d.Game



def traceStart():
    tracemalloc.start()

def logTrace():
    snapshot=tracemalloc.take_snapshot()
    #快照对象的统计
    top_stats=snapshot.statistics('lineno')
    for i in top_stats:
        DEBUG_MSG(i)
