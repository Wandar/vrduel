# -*- coding: utf-8 -*-
from __future__ import annotations

import sys

from KBEngine import *

from ServerDeploy import s_ServerDeploy
from c.ComponentBA import ComponentBA
from util import *
from annos import *


class VoiceManagerBA(ComponentBA):
    voiceServers=None
    """
    {
        VOICEADDRESS:{"spaces":{spaceID:playerCnt,},"allPlayerCnt":323}
    }
    """
    def onLoad(self):
        globalData["VoiceManagerBA"]=self
        self.voiceServers={}
        if not isDebugVer():
            self.getAllVoiceServer()


    def getAllVoiceServer(self):
        for machineJ in s_ServerDeploy().machines:
            machineIP=machineJ["externalIP"]
            for appJ in machineJ["appList"]:
                if appJ["type"]=="voice":
                    addr=machineIP+':'+appJ["cid"]
                    self.voiceServers[addr]={"spaces":{},"allPlayerCnt":0}

    #p CALL
    def reqFreeVoiceAddress(self,spaceCE):
        if len(self.voiceServers)==0:
            spaceCE.onReqFreeVoiceAddress("")
            return
        minnum=9999999
        minaddress=""
        for voiceaddress,j in self.voiceServers.items(): #得到人最少的
            if j["allPlayerCnt"]<minnum:
                minnum=j["allPlayerCnt"]
                minaddress=voiceaddress
        if not minaddress:
            ERROR_MSG("reqFreeVoiceAddress no voice address")
            return
        spaceCE.onReqFreeVoiceAddress(minaddress)


    #p ID STRING UINT32
    def sendVoiceAddressPlayerCnt(self,roomUniID,voiceAddress,playerCnt):
        if voiceAddress not in self.voiceServers:
            return
        self.voiceServers[voiceAddress]["spaces"][roomUniID]=playerCnt

        #cal all players
        self.voiceServers[voiceAddress]["allPlayerCnt"]=0
        for i,cnt in self.voiceServers[voiceAddress]["spaces"].items():
            self.voiceServers[voiceAddress]["allPlayerCnt"]+=cnt



    #p ID STRING
    def delVoiceAddressPlayerCnt(self,roomUniID,voiceAddress):
        if voiceAddress not in self.voiceServers:
            return
        del self.voiceServers[voiceAddress]["spaces"][roomUniID]

        #cal all players
        self.voiceServers[voiceAddress]["allPlayerCnt"]=0
        for i,cnt in self.voiceServers[voiceAddress]["spaces"].items():
            self.voiceServers[voiceAddress]["allPlayerCnt"]+=cnt
