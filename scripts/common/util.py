# -*- coding: utf-8 -*-
import io
import platform
import sys

import KBEngine
import math
import copy
from Math import *
from KBEDebug import *
import re
#from ServerDeploy import * 莫名其妙没有用
from UserType import *
from dataLoader import *
from fastFunc import *
from utils.VectorFunc import *
from ServerConstants import *
from config import *
from reloadSystem import *
from typing import *
from annos import *
from vec import *

if 0:from KBEMath.Math import *
if 0:from cellapp.KBEngine import *
if 0:from baseapp.KBEngine import *

import time
import json
import hashlib

class AClass:
    ddbb=12
    pass

#100000次 UserType创建6s
#100000 dict 0.08s

#100000次创建新
#100000次把ATTR转入dict来创建dict 0.45
#100000次**方式的ItemData

#100000 getComponent 2s
#100000 getCOm不拼接 1.3s
#100000 hasattr 存在0.6 不存在0.9 直接拼接好像不消耗时间
#100000 en.leftPressTid 0.55
#100000 lower() 0.04
#100000 _components改进 1.6s
#100000 外部执行0.05900的代码在引擎里面变成了0.25 # 但是交给Entity来执行几乎一样的代码,就变成了1.6s,我觉得是因为类的深度巨大
#100000 onMove 带有组件检查的4.8s 不带组件的0.8s

#100000 a+=1 0.03

#100000 dict 0.075
#100000 MyType 0.3

#10000 Entity设置C++层的 0.066  随便一个属性设置也是0.066 getRad方法调用也是0.066,
        #随便一个方法调用也是0.066,修改后0.2
#10000 普通类的方法调用0.004,普通类的属性赋值0.001
#10000 方法调用const char*再查def和普通的PyUnicode_AsWideCharString差不多都是 0.06
#1000000 getPos 0.78

#expand 500个子弹 169ms
#200个bullet 一个单位 10000交叉setPos 0.148
#4000个bullet  也是0.148,貌似毫无影响,可能是因为加在了链表的最上层


#在kbe里运行
# a=0
# for i in range(1000):
#     for j in range(100):
#         a+=1
# 我的电脑
# 0.059003353118896484
# linux
# 0.004736423492431641

#1000 getPos 0.001
#1000 setInterval 0.62
#1000 增删定时器 0.018


class Busy:
    t=0
    lastTime=0
    def __init__(self,lastTime):
        self.t=time.time()
        self.lastTime=lastTime

    def checkIsBusy(self):
        if time.time()-self.t>=self.lastTime:
            return False
        return True

    def setBusy(self,lastTime):
        self.t=time.time()
        self.lastTime=lastTime


def test(a):
    DEBUG_MSG("test")
    t1 = time.time()
    for i in range(1000):
        # id=a.setInterval(1,0,noFunc)
        # a.delInterval(id)
        a.addTimer(1,0,100)
        # a.getPos()
    t2 = time.time()
    DEBUG_MSG(t2 - t1)


import inspect
def getFuncName():
    return inspect.stack()[1][3]



def numpyShuffle(l):
    random.shuffle(l)

def noFunc(tid):
    pass


def filterEmoji(comment):
    return str(bytes(comment, encoding='utf-8').decode('utf-8').encode('gbk', 'ignore').decode('gbk'))


class TestClass:
    fuu=12
    def __init__(self):
        self.fuu=33



class Rect:
    __slots__ = ('x','y','width','height','xMax','yMax')
    def __init__(self,x,y,width,height):
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.xMax=x+width
        self.yMax=y+height

    def containPoint(self,pos):
        if self.x<=pos[0]<=self.xMax and self.y<=pos[1]<=self.yMax:
            return True
        return False



def limit(num, min_value, max_value):
    return max(min(num, max_value), min_value)


def limitCal(num,cal,min,max):
    num=num+cal
    if num<min:
        min=min
    elif num>max:
        num=max
    return num


def uint8ToScale(uint8):
    return uint8/100

def scaleToUint8(scale):
    uint8=math.floor(scale*100)
    if uint8<0 or uint8>255:
        ERROR_MSG("too big scale")
        uint8=100
    return uint8

def int8ToRad(int8):
    return int8 * (math.pi / 128.0)

def radToInt8(rad):
    int8 = math.floor((rad * 128.0) / math.pi + 0.5)
    if int8==128:
        int8=-128
    return int8


def fuzzyEqual(a,b,f=0.001):
    return abs(a-b)<f

def radFuzzyEqual(a,b,f=0.001):
    return abs(normaliseRad(a-b))<f

# def initEnv():
#     os.

# def tryFunc(obj,funcName,*args):
#     func=getattr(obj,funcName,None)
#     if func:
#         return func(*args)
#     else:
#         return False

def setattrIfNot(obj,attrName,val):
    if getattr(obj,attrName)!=val:
        setattr(obj,attrName,val)

def calRandJsonAllValue(j):
    allW=0
    for a in j:
        allW+=j[a]
    return allW

#从dict中随机取出一个,{key:weight},返回key
def randDictWeight(j, allW=0):
    if allW==0:
        for a in j:
            allW+=j[a]

    rad=random.uniform(0,allW)
    cur=0
    for a in j:
        cur+=j[a]
        if rad<cur:
            return a

#从Dict中随机选取,{key:{weight:value}}
def randDictWithWeight(dic,weightStr="weight",allW=0):
    if not allW:
        for id,j in dic.items():
            allW+=j[weightStr]
    rad=random.uniform(0,allW)
    cur=0
    for id,j in dic.items():
        cur+=j[weightStr]
        if rad<cur: #不用改<=
            return id

#从List随机,[{weight:value}]
def randListDictWithWeight(l,weightStr="weight",allW=0):
    if not allW:
        for d in l:
            allW+=d[weightStr]
    rad=random.uniform(0,allW)
    cur=0
    for d in l:
        cur+=d[weightStr]
        if rad<cur: #不用改<=
            return d
    ERROR_MSG("randListDictWithWeight")
    return l[-1]

# def randWithWeight(array,wightArr):
#     allW=0
#     for a in wightArr:
#         allW+=a
#
#     rad=random.uniform(0,allW)
#     cur=0
#     result=0
#     for i in range(len(wightArr)):
#         a=wightArr[i]
#         cur+=a
#         if rad<cur:
#             result=i
#             break
#     return array[result]

def floatEqual(a,b):
    if abs(a-b)<0.0001:
        return True
    else:
        return False

def isWindows():
    return "Windows" in platform.platform()

def delGlobalG(name):
    if name in KBEngine.globalData:
        del KBEngine.globalData[name]

def openRes(resUrl,rw):
    return io.open(KBEngine.getResFullPath(resUrl),rw,encoding="utf-8")

def listToDict(l,keyName="id"):
    dic={}
    for i in l:
        dic[i[keyName]]=i
    return dic



def normaliseRad(r):
    cnt=0
    while 1:
        if r>math.pi:
            r-=2*math.pi
        elif r<-math.pi:
            r+=math.pi*2
        else:
            return r
        cnt+=1
        if cnt>500:
            return r

def checkBase():
    if not hasattr(KBEngine, "kbetime"):
        sys.exit()
    return KBEngine.isDebugVer()


def getFileLastModifyTime(filePath):
    return time.ctime(os.path.getmtime(filePath))

"""
os func
"""
import socket
def getHostName():
    return socket.gethostname()

"""
time func
"""
def isOutTimePeriod(time1, sec):
    return time.time()-time1>sec

def checkArg(self, argName):
    if hasattr(self, argName):
        ERROR_MSG("already has arg%s" % argName)



# 10000 vector3 flatDistTo 0.00699
# 10000 vector3 手工的flatDistTo 0.05
# 10000 预先设定mathVector3,然后把数组带进去算,0.04

# 1000000 None 0.2
# 1000000 a+b 0.25
# 1000000 一个func 0.5
# 1000000 2个func 0.8
# 1000000 3ge func 1.1
# 调用一个func需要0.3 us
# 1000000 try func不存在的 3s


def test4():
    pass


def test3():
    test4()
    pass


# def test2():
#     test3()
#     pass


# mathVector3 = Vector3(0, 0, 0)
# mathVector32 = Vector3(0, 0, 0)
class TestA:
    def aa(self):
        pass

def testPLEn(v):
    return math.sqrt(v[0]*v[0]+v[1]*v[1])



#用在Reload上有问题
# def isSubClassOf(obj, cls):
#     try:
#         for i in obj.__bases__:
#             if i is cls or isinstance(i, cls):
#                 return True
#         for i in obj.__bases__:
#             if isSubClassOf(i, cls):
#                 return True
#     except AttributeError:
#         return isSubClassOf(obj.__class__, cls)
#     return False

def isSameClass(obj,cls):
    return obj.__class__.__name__==cls.__name__

"""
basic func
"""

#弧度取反
def radNeg(rad):
    if rad>0:
        return rad-math.pi
    else:
        return math.pi+rad


# 减去返回大于0的float
def sub0f(num, sub):
    if num > sub:
        return float(num - sub)
    else:
        return float(0)


def sub0(num, sub):
    if num > sub:
        return num - sub
    else:
        return 0


# 是否被破坏
def isValid(obj):
    if not obj or obj.isDestroyed or obj.isDestroying:
        return False
    else:
        return True


def calAByVAndL(v,l):
    return -v*v/2/l

def getClassAttrName(CLASS,value):
    for key,v in CLASS.__dict__.items():
        if v==value:
            return key
    ERROR_MSG("getClassAttrName no attr in CLASS ",CLASS.__name__)
    return None

def getKeyByValue(j, key):
    for i in j:
        if j[i]==key:
            return i
    ERROR_MSG("getKeyByValue no key in value ",key)
    return None

def randPos(xMin, xMax, yMin, yMax):
    return (random.randint(xMin, xMax), random.randint(yMin, yMax))


def randPosInCircle(pos,radius):
    rad=random.uniform(-math.pi,math.pi)
    d=radiansToVector2(rad)
    l=random.randint(0,radius)
    d=pMult(d,l)
    return pAdd(pos,d)

def randDictKey(dic):
    if len(dic):
        return random.choice(list(dic))
    else:
        return None

def randDict(dic):
    if len(dic):
        return dic[randDictKey(dic)]
    else:
        return None


def randList(l):
    return random.choice(l)

def randRad():
    return random.uniform(-math.pi,math.pi)

def randBool():
    if random.random()>0.5:
        return True
    else:
        return False

def randSymbol():
    if random.random()>0.5:
        return 1
    else:
        return -1

def idDictToList(dic):
    l=[]
    for id,j in dic.items():
        j["id"]=id
        l.append(j)
    return l

def idListToDict(l):
    dic={}
    for j in l:
        dic[j["id"]]=j
    return dic


#{1:2}+{1:3}={1:5}
def numDictAdd(m,n):
    r={}
    for i,num in m.items():
        r[i]=num
    for i,num in n.items():
        if i in r:
            r[i]+=num
        else:
            r[i]=num
    return r

_timeCode=0
def timePre():
    global _timeCode
    _timeCode=time.time()

def timeLog(msg=""):
    INFO_MSG(msg+" usedTime=",time.time()-_timeCode)

"""
# rand func

"""


def randPercent(percent):
    if percent > random.random():
        return True
    else:
        return False


# uniform
# def randFloat():


"""
#加密,压缩
"""


def md5(s):
    m=hashlib.md5()
    s=s.encode("utf-8")
    m.update(s)
    return m.hexdigest()


"""
游戏相关
"""

"""
# 数据便利功能
"""


def jsonItemSpaceData(id, quality, ammoCnt):
    return {
        "id": id,
        "quality": quality,
        "enhance": 0,
        # 千万注意这个
        "cd": 0.0,
        "ammoCnt": ammoCnt,
        "isEquipped": 0
    }


def jsonItemSpaceNull():
    return {
        "id": 0,
        "quality": 0,
        "cd": 0.0,
        "enhance": 0,
        "ammoCnt": 0,
        "isEquipped": 0
    }


#破坏整个dict内的单位
def destroyAllDict(l, destroyFuncName, *args):
    temp=[]
    for i,j in l.items():
        temp.append(j)
    for obj in temp:
        getattr(obj,destroyFuncName)(*args)

def destroyAllList(l, destroyFuncName, *args):
    temp=[]
    for j in l:
        temp.append(j)
    for obj in temp:
        getattr(obj,destroyFuncName)(*args)

def listDelBy(l,attrName,val):
    needDelID=None
    for i in range(len(l)):
        if l[i][attrName]==val:
            needDelID=i
            break
    if needDelID is not None:
        del l[needDelID]
        return True
    else:
        return False
"""
base fastFunc
"""




#for reloadScript
#不能用于没有self的方法
class FunctorReload:
    __slots__ = ("this","funcName","args")
    def __init__(self, func:"function", *args):
        self.this=func.__self__
        self.funcName = func.__name__
        self.args = args

    def __call__(self, *args):
        return getattr(self.this,self.funcName)(*(self.args + args))

class Functor:
    __slots__ = ("func","args")
    def __init__(self, func, *args):
        self.func=func
        self.args = args

    def __call__(self, *args):
        return self.func(*(self.args + args))

#用于给方法没有tid参数的方法添加
class FunctorTid:
    __slots__ = ("func","args")
    def __init__(self,func:"function",*args):
        self.func=func
        self.args=args
        pass

    def __call__(self,tid):
        return self.func(*self.args)

def mergeJsonTo1(json1,json2):
    for i in json2:
        if i in json1:
            ERROR_MSG("merge conflict ",i)
        json1[i]=json2[i]

#去除了'=',base64最后一位
DIRTY_STUFF = [
    "\"", "\\", "/", "*", "'", "-", "#", ";", "<", ">", "+", "%", "$", "(", ")", "%","!"]

def sqlFilter(string):
    for stuff in DIRTY_STUFF:
        string = string.replace(stuff, "")
    return string


def checkUserNameLegal(s):
    if re.match(r"^[a-zA-Z0-9_@.]+$", s) and 50 > len(s) > 3:
        return True
    else:
        return False

#cant be ""
def checkPasswdLegal(s):
    if re.match(r"^[a-zA-Z0-9=]+$", s) and 255 > len(s) > 3:
        return True
    else:
        return False

def checkStringSQLSafe(string:str):
    for stuff in DIRTY_STUFF:
        if string.find(stuff)!=-1:
            return False
    return True

#是否都是数字
def isStrAllNumber(string):
    if re.match(r"^[0-9]+$",string):
        return True
    else:
        return False


def checkIsGuestAccount(string):
    if string[0:6]=="guest_" and string[-4:]=="@0.0":
        return True
    else:
        return False

def checkEMailUserNameValid(email):
    if len(email)<3 or len(email)>255:
        return False
    if re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
        return True
    else:
        return False


def checkJsonValid(j,nameTuple):
    for name in nameTuple:
        if name not in j:
            return False
    return True


def reverse64Bits(n: int) -> int:
    ans = 0
    for i in range(64):
        ans = (ans << 1) | (n & 1)
        n >>= 1
    return ans

def number64toStr(num):
    txt=""
    a=10
    b=str(num)
    c=32

    lis = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
           'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U','V']

    result = sum(a ** i * lis.index(b.upper()[::-1][i]) for i in range(len(b)))  # 2-32任意进制 转 10进制

    while bool(result):  # 10进制 转 2-32任意进制
        txt += lis[result % c]
        result //= c
    return txt[::-1]

def strToNumber64(s):
    txt=""
    a=32
    b=s
    c=10

    lis = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
           'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U','V']

    result = sum(a ** i * lis.index(b.upper()[::-1][i]) for i in range(len(b)))  # 2-32任意进制 转 10进制

    while bool(result):  # 10进制 转 2-32任意进制
        txt += lis[result % c]
        result //= c
    return int(txt[::-1])

#
#
# def arrDictSetItem(arr,key, value):
#     if key in self:
#         i=self._isKeyInList(key)
#         del self.list[i]
#     self.list.append(value)
#     dict.__setitem__(self,key,value)
#
#
# class ListDict(dict):
#     keyName="id"
#     list=None
#     def __init__(self,keyName="id"):
#         dict.__init__(self)
#         self.keyName=keyName
#         self.list=[]
#
#     def __setitem__(self, key, value):
#         if key in self:
#             i=self._isKeyInList(key)
#             del self.list[i]
#         self.list.append(value)
#         dict.__setitem__(self,key,value)
#
#     #返回序号,不存在返回None
#     def _isKeyInList(self,key):
#         for i in range(len(self.list)):
#             if getattr(self.list[i],self.keyName)==key:
#                 return i
#         return None
#
#     def __delitem__(self, key):
#         dict.__delitem__(self,key)
#         i=self._isKeyInList(key)
#         del self.list[i]
#
#     def clear(self):
#         dict.clear(self)
#         self.list=[]