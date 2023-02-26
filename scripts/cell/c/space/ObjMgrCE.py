# -*- coding: utf-8 -*-
from KBEngine import *

from c.space.SpaceComponentCE import SpaceComponentCE
from util import *
from annos import *


class Stored:
    EXPAND_NUM=10
    SHOULD_NUM=0
    list=None #库存中的对象,active后会从中删除
    actives=None #使用中的
    def __init__(self,shouldNum,expandNum=1,canReinit=False):
        self.SHOULD_NUM=shouldNum
        self.EXPAND_NUM=expandNum
        self.list=[]
        self.actives={}
        self.canReinit=canReinit

    def reinit(self):
        if self.canReinit:
            for id,obj in self.actives.items():
                obj.onReinit()
        else:
            for obj in list(self.actives.values()):
                obj.store()

    def cleanList(self):
        s=""
        if len(self.list):
            s=self.list[0].__class__.__name__
        elif len(self.actives):
            s=randDict(self.actives).__class__.__name__
        INFO_MSG('destroy Stored %s Obj %d Active %d'%(s,len(self.list),len(self.actives)))
        for en in self.list:
            en.tryDestroy()
        self.list=[]
        for id,en in self.actives.items():
            en.tryDestroy()
        self.actives={}

IS_DESTROY_ENABLED=False #测试回收时直接破坏,如果需要破坏就是True

class ObjMgrCE(SpaceComponentCE):
    stores=None  #name:Stored
    def onLoad(self):
        # self.stores={
        #     "Bullet":Stored(200,1),
        #     "NormalObstacle":Stored(200,1,canReinit=True),
        #     "Item":Stored(200,1),
        #     "Door":Stored(100,canReinit=True),
        #     "DeathBox":Stored(100),
        # }
        self.stores={
            "CardEntity":Stored(0,1),
            "Hand":Stored(0,1)
        }

        # self.setInterval(0.1, ADD_ENTITY_TIME, self.onTimerSpaceExpandEntities)

    def getStoredObj(self,className):
        stored=self.stores[className]
        if len(stored.list) == 0:
            self._expandObj(className,1)
        obj=stored.list[0]
        del stored.list[0]
        stored.actives[obj.id] = obj
        obj.active=True
        obj.isDestroying=False
        obj.setCoorEnabled(True)
        return obj


    def onTimerSpaceExpandEntities(self, tid):
        allFinish = True
        for name,stored in self.stores.items():
            if len(stored.list)+len(stored.actives)<stored.SHOULD_NUM:
                self._expandObj(name,stored.EXPAND_NUM)
                if allFinish:
                    allFinish=False
        if allFinish:
            self.delInterval(tid)


    def reinitSpaceObjMgr(self):
        for name,stored in self.stores.items():
            stored=stored #type:Stored
            stored.reinit()

    # def y_reinitSpaceObjMgr(self):
    #     yield "wait" #必须是协程
    #     num=0
    #     for name,stored in self.stores.items():
    #         stored=stored #type:Stored
    #         if stored.canReinit: #障碍物应该是reinit而不是store
    #             funcName="onReinit"
    #         else:
    #             funcName="store"
    #
    #         for obj in list(stored.actives.values()):
    #             func=getattr(obj,funcName)
    #             func()
    #             num+=1
    #             if num>50:
    #                 #DEBUG_MSG("reinit Space Obj 50")
    #                 num=0
    #                 yield "wait"




    def getStoredNum(self,className):
        stored=self.stores[className]
        return len(stored.list)

    #200个子弹 1000次 0.169
    #4700个子弹 1000次  一开始0.35,后面加到1.3
    #修改后不管怎样都是 0.23
    # def testObjPerformance(self):
    #     ti=time.time()
    #     for i in range(1000):
    #         bullet=self.getStoredObj("Bullet")
    #         bullet.setPosXY(500,500)
    #         bullet.setCoorEnabled(True)
    #         self.storeObj(bullet)
    #     DEBUG_MSG("use time t=",time.time()-ti)

    def _expandObj(self, className,num):
        for i in range(num):
            obj= createEntity(className, self.spaceID, OUTER_POS, 0,{"POOLOBJ":True,"active":False})
            obj.setCoorEnabled(False)
            self.stores[className].list.append(obj)

    def storeObj(self, obj):
        if not IS_DESTROY_ENABLED:
            # MeleeBox.setPosXYZ(MeleeBox.outerX,0,MeleeBox.outerZ)
            #注意 这里用append的话如果子弹被回收后立刻使用,会在客户端留下影子
            stored=self.stores[obj.className] #type:Stored
            if obj.id in stored.actives:
                obj.controlledBy=None
                obj.stopMoveAndTurn()
                obj.onStoreObj()
                obj.setPos(OUTER_POS)
                obj.setCoorEnabled(False)
                del stored.actives[obj.id]
            else:
                WARNING_MSG("store obj activelist not has ",obj.id)
            stored.list.append(obj)
        else:
            stored=self.stores[obj.className] #type:Stored
            if obj.id in stored.actives:
                obj.controlledBy=None
                obj.stopMoveAndTurn()
                obj.onStoreObj()
                obj.destroy()
                del stored.actives[obj.id]
            else:
                WARNING_MSG("store obj activelist not has ",obj.id)



    def onDestroy(self):
        for name,stored in self.stores.items():
            stored.cleanList()
