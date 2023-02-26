# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2017 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2017/9/14 17:10

from KBEngine import *

from globalEventSystem import fire_reloadData, fire_reloadServerDeploy
from util import *
from c.ComponentBA import ComponentBA


class DataLoaderManagerBA(ComponentBA):
    _dataFileModDatas=None #dataFilePath:modfileData
    def onLoad(self):
        try:
            self._dataFileModDatas={}
            interval=1

            l=self.listDataFile()
            for i in l:
                filemodTime=getFileLastModifyTime(i)
                self._dataFileModDatas[i]=filemodTime


            if not publish():
                self.setInterval(interval,interval,self.dataLoaderTimer)
        except Exception:
            if isWindows():
                WARNING_MSG("DataLoader init error perhaps VS Debug")
            else:
                ERROR_MSG("DataLoader err")

    def listDataFile(self):
        return (
            getResFullPath("server_common/D_CARD.json"),
        )

    #重载数据
    def dataLoaderTimer(self,tid):
        shouldReload=False
        l=self.listDataFile()
        for i in l:
            filemodTime=getFileLastModifyTime(i)
            if i not in self._dataFileModDatas:
                self._dataFileModDatas[i]=0
            if self._dataFileModDatas[i]!=filemodTime:
                INFO_MSG("%s changed"%i)
                shouldReload=True
                self._dataFileModDatas[i]=filemodTime
        if shouldReload:
            fire_reloadData()



    def onDestroy(self):
        pass