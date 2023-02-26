# -*- coding: utf-8 -*-
import types
import time

from Constants import ERR_TIME_OVER
from KBEDebug import *

CONSUMED_CALLBACK=1
NOT_MATCH=2
CONSUMED_AND_OVER=3
ERR_REMOVE=4

class CBBase:
    name=""
    def __init__(self,overTime):
        self.overTime=overTime
        self.startTime=time.time()

    def isOverTime(self):
        if not self.overTime:
            return False
        return time.time()-self.startTime>self.overTime

    def satisfy(self,cbName,args):
        return False

    def getResult(self,arg):
        return _formatArgs(arg)

    def getTimeOutResult(self):
        return

#为了实现协程内的超时机制而做了这个
class CBTimeout(CBBase):
    #如果cbName不是函数名,argNum要写参数个数,回调函数的参数第一个肯定是err
    def __init__(self,cbName,argNum,overTime=1):
        CBBase.__init__(self,overTime)
        self.name=cbName
        self.argNum=argNum

    def satisfy(self,cbName,args):
        if cbName==self.name:
            return True
        return False

    def getTimeOutResult(self):
        a=(ERR_TIME_OVER,)
        for i in range(self.argNum-1):
            a+=(None,)
        a=_formatArgs(a)
        return a


class WaitForAll(CBBase):
    name="AllCor"
    def __init__(self,cbNameTuple:tuple,overTime=1):
        CBBase.__init__(self,overTime)
        self.cbs={}
        for name in cbNameTuple:
            self.cbs[name]=False

        self.returns={}

    def _isAllCBComplete(self):
        for cbName,isComplete in self.cbs.items():
            if not isComplete:
                return False
        return True

    def satisfy(self,cbName,args):
        if cbName in self.cbs:
            self.cbs[cbName]=True
            self.returns[cbName]=_formatArgs(args)
            if self._isAllCBComplete():
                return True
        return False

    def getResult(self,arg):
        return self.returns

    def getTimeOutResult(self):
        return ERR_TIME_OVER

def _formatArgs(args):
    if len(args)==0:
        return None
    elif len(args)==1:
        return args[0]
    return args


class CoroutineUnit:
    """
    每一个generator，都包装成CoroutineUnit
    """
    def __init__(self, fun, overTimeFunc=None, overTime=10, overError=False):
        self.overTimeFunc=overTimeFunc
        self.startTime=time.time()
        self.overTime=overTime
        self.name=fun.__name__
        self._generatorStack = []
        self._generatorStack.append(fun)
        self.overError=overError
        # self.lastReturnTime=time.time()

        #当前处于的位置,有可能是callbackName,也有可能是其他generator
        self.current=self._generatorStack[-1].send(None)
        while 1: #处理开头的协程嵌套
            if isinstance(self.current,types.GeneratorType):
                self._generatorStack.append(self.current)
                self.current=self._generatorStack[-1].send(None)
            else:
                break

    def hasStack(self):
        return len(self._generatorStack)

    def isOverTime(self):
        if not self.overTime:
            return False
        return time.time()-self.startTime>self.overTime


    # def refresh(self,callbackName,args):
    #     hasReturnValue=False
    #     returnValue=None
    #     while 1:
    #         if type(self.current)==str:
    #             if self.current



    def refresh(self,callbackName,args):
        if type(self.current)==str: #如果是str那么只有匹配后才能下去
            if self.current!=callbackName:
                return NOT_MATCH
            args=_formatArgs(args)

        elif isinstance(self.current, CBBase):
            if self.current.satisfy(callbackName,args): #如果是CB而且匹配
                args=self.current.getResult(args)
                pass
            elif callbackName=="wait" and self.current.isOverTime(): #如果是CB,而且callback是wait而且CB超时了
                WARNING_MSG("CBTimeout overTime ",self.name,self.current.name)
                args=self.current.getTimeOutResult()
            else:
                return NOT_MATCH  #不能下去
        elif isinstance(self.current,types.GeneratorType):#开头处理过了,这里不应该进来
            ERROR_MSG("current is GeneratorType")
            self._generatorStack=[]
            return ERR_REMOVE
        else:
            ERROR_MSG("self current not type ",self.current)
            self._generatorStack=[]
            return ERR_REMOVE


        hasReturnValue=False #堆栈其他generator是否有返回值
        returnValue=None #堆栈内压入的其他generator的返回值

        try:
            self.current=self._generatorStack[-1].send(args)
        except StopIteration as e:
            self._generatorStack.pop()
            if len(self._generatorStack):
                self.current=self._generatorStack[-1]
                hasReturnValue=True
                returnValue=e.value
            else:
                return CONSUMED_AND_OVER

        while 1:
            if hasReturnValue: #如果是完成的堆栈
                hasReturnValue=False
                try:
                    self.current=self._generatorStack[-1].send(returnValue)
                except StopIteration as e:
                    self._generatorStack.pop()
                    if len(self._generatorStack):
                        self.current=self._generatorStack[-1]
                        hasReturnValue=True
                        returnValue=e.value
                    else:
                        return CONSUMED_AND_OVER
            #如果是等待的函数,不能是函数因为可能需要%上其他参数
            elif type(self.current)==str or isinstance(self.current, CBBase):
                # self.lastReturnTime=time.time()
                return CONSUMED_CALLBACK
            #如果是其他generator就压栈
            elif isinstance(self.current, types.GeneratorType):
                self._generatorStack.append(self.current)
                self.current=self._generatorStack[-1].send(None)
            else:#必须是协程
                ERROR_MSG("error MyCoroutine yield not CBTimeout or generator",self.current)
                self._generatorStack=[]
                return ERR_REMOVE

    def close(self):
        for cor in self._generatorStack:
            cor.close()
        self._generatorStack.clear()

class CorouCallBack:
    def __init__(self,name,*args):
        self.name=name
        self.args=args
        self.time=time.time()

# COROUTINE_MAX=500
CB_OVER_TIME=1.1 #回调到了之后1.1s不被消耗掉就报错

#wait的时间间隔0.25s,但是不是固定的,可能会小,在等待回调之间千万不要wait
class MyCoroutine:
    """
    需要用到协程的类（从KBEngine.Entity或者KBEngine.Base派生的类），只需要继承自这个类，然后调用StartCoroutine即可开启协程
    """
    _corCheckTid=0
    _checkTimeDelCnt=0
    _coroutineList=None
    _callbackList=None
    def __init__(self):
        #只能用List因为name可能重复
        self._coroutineList = []
        self._callbackList=[]

    def resetCoroutine(self):
        self._coroutineList=[]
        self._callbackList=[]
        self._checkTimeDelCnt=0
        if self._corCheckTid:
            self.delInterval(self._corCheckTid)
            self._corCheckTid=0


    #fun应该是已经调用的函数,而不是函数本身,必须带有一个yield
    #overTimeCB是超时出错后的函数,参数是卡死处的字符串,要做的是恢复现场,比如给其他单位加锁了,要在里面解锁
    #overError指是否提示超时错误
    def startCoroutine(self, fun, overTimeCB=None, overTime=10, overError=False,isUnique=False):

        # DEBUG_MSG("fun ",fun)

        if isUnique:
            if self.hasCoroutine(fun.__name__):
                WARNING_MSG("coroutine already has ",fun.__name__)
                return

        # if len(self._coroutineList)>COROUTINE_MAX:
        #     ERROR_MSG("too many coroutine ",self,fun.__name__)
        #     return

        self._coroutineList.append(CoroutineUnit(fun, overTimeCB, overTime, overError))
        if not self._corCheckTid:
            self._corCheckTid=self.setInterval(0.1, 0.1, self.onTimerDelayFunc)
            self._checkTimeDelCnt=0

    #不能用isUnique,因为外面会执行函数
    def hasCoroutine(self,name:str):
        for cor in self._coroutineList:
            if cor.name==name:
                return True
        return False

    def hasAnyCoroutine(self):
        if len(self._coroutineList):
            return True
        return False

    def hasCoroutines(self,*names:str):
        for cor in self._coroutineList:
            if cor.name in names:
                return True
        return False

    #在同一个进程上的话回调是瞬发的,需要把callback压入堆栈,等待下次
    def onCallBack(self,callbackName,*args):
        if self._checkCallBack(callbackName,*args):
            return
        else:
            self._callbackList.append(CorouCallBack(callbackName,*args))

    def _checkCallBack(self,callbackName,*args):
        for i in range(len(self._coroutineList)-1,-1,-1):
            cor=self._coroutineList[i] #type:CoroutineUnit
            result=cor.refresh(callbackName,args)
            if result==CONSUMED_CALLBACK:
                return True
            elif result==CONSUMED_AND_OVER:
                del self._coroutineList[i]
                return True
            elif result==ERR_REMOVE:
                if cor.overTimeFunc:
                    cor.overTimeFunc(cor.current)
                cor.close()
                del self._coroutineList[i]
        return False

    def onTimerDelayFunc(self,tid):
        #check callback
        for i in range(len(self._callbackList)-1,-1,-1):
            cb=self._callbackList[i] #type:CorouCallBack
            if self._checkCallBack(cb.name,*cb.args):
                del self._callbackList[i]
            elif time.time()-cb.time>CB_OVER_TIME:
                WARNING_MSG("onCallback not match any ",cb.name)
                del self._callbackList[i]


        if not len(self._coroutineList):
            self._checkTimeDelCnt+=1
            #超过1秒没有coroutine就删掉这个定时器
            if self._checkTimeDelCnt>10:
                self._corCheckTid=0
                self.delInterval(tid)
                return
        else:
            self._checkTimeDelCnt=0

        for i in range(len(self._coroutineList)-1,-1,-1):
            cor=self._coroutineList[i] #type:CoroutineUnit
            result=cor.refresh("wait",())
            if result==CONSUMED_AND_OVER:
                del self._coroutineList[i]
            elif result==CONSUMED_CALLBACK:
                pass
            elif cor.isOverTime(): #overTime,wait时不会进到这里
                if cor.overError:
                    ERROR_MSG("coroutine overTime ",cor.name,cor.current)
                else:
                    WARNING_MSG("coroutine overTime ",cor.name,cor.current)
                del self._coroutineList[i]
                if cor.overTimeFunc:
                    cor.overTimeFunc(cor.current)
                cor.close()
            elif result==ERR_REMOVE:
                del self._coroutineList[i]
                if cor.overTimeFunc:
                    cor.overTimeFunc(cor.current)
                cor.close()

    #因为可能destroy也在被cor调用所以不使用这个函数
    #因为使用tryDestroy,所以destroy时不应该有任何的cor
    def closeAll(self):
        for i in range(len(self._coroutineList)-1,-1,-1):
            cor=self._coroutineList[i] #type:CoroutineUnit
            WARNING_MSG("onDestroy with generator leave ",cor.name)
            del self._coroutineList[i]
            if cor.overTimeFunc:
                cor.overTimeFunc(cor.current)
            cor.close()

    def corOnDestroy(self):
        # self._coroutineList=None
        pass


