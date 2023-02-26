# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2017 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2017/9/11 19:23

from KBEngine import *
from util import *
from c.CheckTime import CheckTime
from c.Component import Component
from c.MyCoroutine import MyCoroutine

if 0:from baseapp import KBEngine


#所有Base的Component继承自这个,所有的COmponent不允许有__init__
#注意这个类的__init__并没有init Base
class ComponentBA(KBEngine.Entity, Component, CheckTime, MyCoroutine, Reload):
    isDestroying=False

    OVERRIDE_LOSE_CELL=False #随着cell一起被破坏
    #hasCell=False

    # noinspection PyMissingConstructor
    def __init__(self):
        pass

    def _initBaseComponent(self):
        #这里是可以的
        if issubclass(self.__class__,Proxy):
            Proxy.__init__(self)
        else:
            Entity.__init__(self)
        Component.__init__(self)
        CheckTime.__init__(self)
        MyCoroutine.__init__(self)
        Reload.__init__(self,False,True)
        self.onLoad()
        self.setInterval(0,0,self.onTimerStart)

    def baseOnLoad(self):
        pass

    def onTimerStart(self,tid):
        pass

    # def callCellMustReach(self,cellFuncName,*args):
    #     timeouttime=10
    #     if self.cell:
    #         getattr(self.cell,cellFuncName)(*args)
    #     else:
    #         # self.setInterval(0,0.1,Functor(self._onTimerCallCellMustReach,cellFuncName,time.time()+timeouttime,*args))
    #         self.setInterval(0,0.1,self._onTimerCallCellMustReach,(cellFuncName,time.time()+timeouttime,args))
    #
    # def _onTimerCallCellMustReach(self,cellFuncName,timeoutDate,*args):
    #     if time.time()>timeoutDate:
    #         ERROR_MSG("_onTimerCallCellMustReach timeout ",cellFuncName)
    #         return DEL_INTERVAL
    #     if self.cell:
    #         getattr(self.cell,cellFuncName)(*args)
    #         return DEL_INTERVAL

    #p
    def tryDestroy(self):
        pass

    def delayDestroy(self):
        self.setInterval(0,0,self.onTimerDestroy)

    def onTimerDestroy(self,tid):
        self.destroy()

    def onServerClose(self):
        pass

    def onWriteToDB(self,cellData):
        pass
    def onLoseCell( self ):
        pass

    def onCellCrash(self):
        pass

    def onGetCell( self ):
        pass
    def onDestroy( self ):
        pass

    def onCreateCellFailure(self):
        pass

    def baseOnDestroy(self):
        MyCoroutine.corOnDestroy(self)
        Component.offAll(self)


