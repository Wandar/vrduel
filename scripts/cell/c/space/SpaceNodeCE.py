# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2017 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2017/10/15 20:15

from KBEngine import *

from c.space.SpaceComponentCE import SpaceComponentCE
from mydicts import mySpaces
from util import *


class SpaceNodeCE(SpaceComponentCE):
    # noinspection PyMissingConstructor
    def __init__(self):
        mySpaces[self.spaceID]=self
        self._initSpaceComponent()


    def onLoad(self):
        self._callAllComFunc("onLoad")

    def onSpaceInited(self):
        self._callAllComFunc("onSpaceInited")

    # def onSpaceGeometryLoaded(self):
    #     self._callAllComFunc("onSpaceGeometryLoaded")

    def onTimerStart(self,tid):
        self._callAllComFunc("start")

    def onServerClose(self):
        self._callAllComFunc('onServerClose')


    def onDestroy( self ):
        self._callAllComFunc("onDestroy")
        del mySpaces[self.spaceID]
        self.spaceOnDestroy()



