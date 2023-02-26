# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2017 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2017/9/12 1:10

from KBEngine import *

from c.ComponentBA import ComponentBA
from util import *


#所有Base单位必须继承这个
class NodeBA(ComponentBA):
    # noinspection PyMissingConstructor
    def __init__(self):
        self._initBaseComponent()

    def onLoad(self):
        self.baseOnLoad()
        self._callAllComFunc("onLoad")

    def onTimerStart(self,tid):
        self._callAllComFunc("start")

    def onLoseCell( self ): #cell闪退时不会
        for Class in self.__class__.__bases__[1:]:
            Class.onLoseCell(self)

        if self.OVERRIDE_LOSE_CELL:
            pass
        else:
            self.destroy()

    def onGetCell( self ):
        #self.hasCell=True
        for Class in self.__class__.__bases__[1:]:
            Class.onGetCell(self)

    def onServerClose(self):
        self._callAllComFunc('onServerClose')


    def onWriteToDB(self,cellData):
        self._callAllComFunc('onWriteToDB',cellData)

    def onCellCrash(self):
        self._callAllComFunc("onCellCrash")
        if not self.OVERRIDE_LOSE_CELL:
            self.delayDestroy() #C++循环

    def tryDestroy(self):
        func=None
        for Class in self.__class__.__bases__[1:]:
            func=getattr(Class,"tryDestroy",None)

        if func:
            func(self)
        else:
            if self.isDestroying or self.isDestroyed:
                return

            if self.OVERRIDE_LOSE_CELL:
                ERROR_MSG("tryDestroy not implent ",self.__class__.__name__)
                return

            self.isDestroying=True
            if self.cell:
                self.destroyCellEntity()
                return
            else:
                self.destroy()


    def onDestroy( self ):
        for Class in self.__class__.__bases__[1:]:
            Class.onDestroy(self)
        self.baseOnDestroy()

    def onCreateCellFailure( self ):
        for Class in self.__class__.__bases__[1:]:
            Class.onCreateCellFailure(self)

        ERROR_MSG("createCellFailure id=%d"%self.id)



