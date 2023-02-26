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

"""
如果压力过高就做成分布式
"""
class AccountManagerBA(ComponentBA):
    storeMessageList=None


    accountsByDBID=None #优先使用这个
    accountsByID=None
    accountsByUNIID=None
    def onLoad(self):
        self.accountsByDBID={}
        self.accountsByID={}
        self.accountsByUNIID={}


    websocketHandler=None
    def saveAllAccountsData(self,mwebsocketHandler):
        self.websocketHandler=mwebsocketHandler
        self._trySendMessage(u'start saveData accountNum=%d'%str(len(self.accountsByDBID)))
        self.setInterval(0,0,self.onTimerSaveData)

    def onTimerSaveData(self,tid):
        cnt=0
        for i in range(500):
            if len(self.accountsByDBID):
                dbid,accountBA=self.accountsByDBID.popitem()
                accountBA.writeToDB()
                cnt+=1
        self._trySendMessage(u'save %d accounts'%cnt)
        if len(self.accountsByDBID):
            self.setInterval(0.1,0,self.onTimerSaveData)
        else:
            self._trySendMessage(u'saved all accounts ok')


    def _trySendMessage(self,message):
        try:
            self.websocketHandler.write_message(message)
        except:
            ERROR_MSG("send message failed")


    #p DBID STRING CALL
    def onPlayerEnter(self,accountDBID,uniID,accountBA):
        self.accountsByDBID[accountDBID]=accountBA
        self.accountsByID[accountBA.id]=accountBA
        self.accountsByUNIID[uniID]=accountBA
        pass

    #p DBID STRING ID
    def onPlayerDestroy(self,accountDBID,uniID,accountID):
        if accountID not in self.accountsByID:
            pass#不报错,关闭时可能没有了
        else:
            del self.accountsByID[accountID]

        if accountDBID not in self.accountsByDBID:
            pass
        else:
            del self.accountsByDBID[accountDBID]

        if uniID not in self.accountsByUNIID:
            pass
        else:
            del self.accountsByUNIID[uniID]

    def getAccountNum(self):
        return len(self.accountsByDBID)


    def sendMessageToPlayer(self,toDBID):
        pass


    """
    好友系统做到baseappData内,除了离线功能做到这个类里面
    好友全局功能:发消息,查看当前状态,请求加入房间,请求加为好友,删除好友
    """


    def onDestroy(self):
        self.accountsByDBID.clear()
        self.accountsByID.clear()
        self.accountsByUNIID.clear()
        pass