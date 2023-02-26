# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2018 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2018-04-05 15:44
from __future__ import annotations
from KBEngine import *
from util import *
from c.ComponentBA import ComponentBA
from annos import *


class GameManagerBA(ComponentBA):
    #c BASE BOOL STORED
    hasCardSuggestion=False
    def onLoad(self):
        globalData["GameManager"]=self

        if not isDebugVer():
            self.writeToDB()
            self.initDB()

        # self.setInterval(1,1,lambda tid:self.testFunc1())

    def initDB(self):
        executeRawDatabaseCommand("""
            CREATE TABLE cardsuggestion
            (
                id int unsigned NOT NULL primary key AUTO_INCREMENT,
                subtitle varchar(500),
                content varchar(20000)
            )
            """,self.sqlcallback)

    def testFunc1(self):
        # DEBUG_MSG(getFuncName())


        for i in range(65520):
            genUUID64()
        DEBUG_MSG("---------------")
        for i in range(20):
            DEBUG_MSG(number64toStr(genUUID64()))


    def sqlcallback(self,result, rows, insertid, error):
        INFO_MSG("sql result",result,rows,insertid,error)
        pass

    def onDestroy(self):
        del globalData["GameManager"]
