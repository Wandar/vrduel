# -*- coding: utf-8 -*-
import KBEngine
from util import *


class _Lock:
    overTime=0
    tid=0
    data=None



#防止用户过度调用call,以及lock相关
class CheckTime:
    _locks=None
    _checkTimes=None
    def __init__(self):
        # Basic

        #Exposed

        #other
        self._locks={}
        self._checkTimes={}
        # {
        #     "chatLocal":{
        #         "turnCD":8,
        #         "lastTime":1231.24
        #     }
        # }
        pass

    #如果调用时间间隔太短,False
    #否则,True
    def checkTime(self,funcName,sec=1):
        now=time.time()
        if funcName not in self._checkTimes:
            self._checkTimes[funcName]={
                "cd":sec,
                "lastTime":now
            }
            return True
        #cd short
        if now-self._checkTimes[funcName]["lastTime"]<self._checkTimes[funcName]["cd"]:
            return False
        else:
            self._checkTimes[funcName]["lastTime"]=now
            self._checkTimes[funcName]["cd"]=sec
            return True

    #是否在cd时间内
    def hasCheckTime(self,funcName):
        now=time.time()
        if funcName not in self._checkTimes:
            return False
        if now-self._checkTimes[funcName]["lastTime"]<self._checkTimes[funcName]["cd"]:
            return True
        else:
            return False


    # def _overTime(self,lName):
    #     func=self._locks["overTimeFunc"]
    #     if func:
    #         func()
    #     del self._locks[lName]

    def _overTimeFunc(self,lockName,overTimefunc,tid):
        ERROR_MSG("overtime ",lockName)
        self.unlock(lockName)
        if overTimefunc:
            overTimefunc()

    """
    进行上锁,如果已经有锁了,返回False,上锁成功返回True
    用unlock解开
    如果overTime为0不进行超时回调
    如果overTimeFunc不设置,也会有超时警告,但是不会有回调,overTimeFunc无参数
    注意:data是这个锁暂存的数据,给unlock取用的
    overTimeFunc可以是非self的方法,可以用Functor,但是不能热更新
    """
    def checkLock(self, lockName, overTimeFunc:"function"=None, data=None, overTime=10, warnHasLock=False):
        if lockName in self._locks:
            if warnHasLock:
                WARNING_MSG("haslock",lockName)
            return False

        if overTime:
            # noinspection PyUnresolvedReferences
            tid=self.setInterval(overTime,0,Functor(self._overTimeFunc,lockName,overTimeFunc))
        else:
            tid=0

        a=_Lock()
        a.overTime=overTime
        a.tid=tid
        a.data=data
        self._locks[lockName]=a
        return True


    def hasLock(self,lockName):
        if lockName in self._locks:
            return True
        else:
            return False

    def hasAnyLock(self):
        if len(self._locks):
            return True
        else:
            return False

    #解锁成功返回data,没有这个lock False
    def unlock(self,lockName,shouldWarn=True):
        if lockName in self._locks:
            # noinspection PyUnresolvedReferences
            self.delInterval(self._locks[lockName].tid)
            data=self._locks[lockName].data
            del self._locks[lockName]
            return data
        else:
            if shouldWarn:
                WARNING_MSG("no has lock ",lockName)
            return UNLOCK_ERROR

    def getLockData(self,lockName):
        if lockName in self._locks:
            return self._locks[lockName].data
        else:
            return None
