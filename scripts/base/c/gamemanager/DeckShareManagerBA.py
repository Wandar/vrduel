# -*- coding: utf-8 -*-
from __future__ import annotations

import sys

from KBEngine import *

from ServerDeploy import s_ServerDeploy
from c.ComponentBA import ComponentBA
from util import *
from annos import *

"""
limit share number to 10 every day
当总数超过100000,删除超过3个月无人下载的卡组
"""
class DeckShareManagerBA(ComponentBA):
    #c BASE UINT64 STORED
    increID=1000
    def onLoad(self):
        pass

    #p
    def shareDeck(self):
        # executeRawDatabaseCommand()
        pass

    def _genDeckID(self):
        self.increID+=1
        return self.increID

    #p
    def getDeckByID(self):
        pass


    def getRandomDecks(self):
        #get lots of random decks from db
        pass

    #p
    def reqRandomDecks(self):
        pass

