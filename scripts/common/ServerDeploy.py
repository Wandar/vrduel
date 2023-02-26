# -*- coding: utf-8 -*-
import os
import KBEngine
import json
import util

from KBEDebug import ERROR_MSG, INFO_MSG
from utils.Singleton import singleton

@singleton
class s_ServerDeploy:
    data=None
    machines=None
    def __init__(self):
        if util.isWindows():
            self.data= {
                "updatehz": 15,
                "country": "en",
                "maxPlayerNum": 200,
            }
            self.machines=[]
        else:
            f=util.openRes("sec/server/serverDeploy.json",'r')
            j=json.loads(f.read())
            f.close()

            self.data=None

            selfServerName=self.getServerName()

            for serverWhole in j["servers"]:
                if "machines" not in serverWhole:
                    continue
                for machineJ in serverWhole["machines"]:
                    if selfServerName==machineJ["name"]:
                        self.data=serverWhole["data"]
                        self.machines=serverWhole["machines"]
            if not self.data:
                ERROR_MSG("not find machine",selfServerName)
                return


    def getServerName(self):
        if util.isWindows():
            selfServerName="LOCAL"
        else:
            selfServerName=os.getenv("SERVER_NAME", "NoServerXXXXXXX")
        return selfServerName

    def getCountry(self):
        if "country" in self.data:
            return self.data["country"]
        return "en"


    def getUpdatehz(self):
        return self.data['updatehz']


    def reload(self):
        INFO_MSG("reload ServerDeploy")
        self.__init__()


