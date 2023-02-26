# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2017 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2017/9/12 0:32

from KBEngine import *

from util import *
from annos import *
from typing import TypeVar
T = TypeVar('T')

class Component:
    _selfEvents=None
    COMPONENTS=None
    def __init__(self):
        self._selfEvents={}

    def onLoad(self):
        pass

    def start(self):
        pass

    def onDestroy(self):
        pass

    def calCOMPONENTS(self):
        selfClass=self.__class__
        c=()
        for Class in self.__class__.__bases__:
            c+=(Class.__name__,)
        selfClass.COMPONENTS=c


    def getCom(self,name:str):
        if not self.COMPONENTS:
            self.calCOMPONENTS()
        if name in self.COMPONENTS:
            return self
        return None

    def _callAllComFunc(self,funcName,*args):
        for Class in self.__class__.__bases__[1:]:
            getattr(Class,funcName)(self,*args)

    #对自身进行
    def on(self,eventName,Com,func):
        if eventName not in self._selfEvents:
            self._selfEvents[eventName]={}
        ComName=Com.__name__
        funcName=func.__name__
        self._selfEvents[eventName][ComName+funcName]=(ComName,funcName)

    #对自身
    def off(self,eventName,Com,func):
        if eventName in self._selfEvents:
            del self._selfEvents[eventName][Com.__name__+func.__name__]

    def offAll(self):
        self._selfEvents.clear()

    #对自身
    def emit(self,eventName,*args):
        if eventName not in self._selfEvents:
            return
        for comNameFuncName,t in tuple(self._selfEvents[eventName].items()):
            ComName=t[0]
            funcName=t[1]
            func=getattr(g_allComponents[ComName],funcName)
            if func:
                func(self,*args)
            else:
                WARNING_MSG("emit not found func ComName=%s,funcName=%s"%(ComName,funcName))

    def registerCB(self,Com,func):
        self.cbs[func.__name__]+=(Com.__name__,)
