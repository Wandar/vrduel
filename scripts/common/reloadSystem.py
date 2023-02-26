# -*- coding: utf-8 -*-
import inspect
import os
import importlib
import copy
import weakref
import KBEngine

from KBEDebug import *
import xml.etree.ElementTree as ET
if 0:
    from baseapp import KBEngine
if 0:
    from cellapp import KBEngine



#需要把文件加入热更新黑名单
_blackList=["reloadSystem","mydicts","UserType","cards.allcards"]


"""
热加载规则:
b文件
from a import a
那么a文件应该优先加载


*列表顺序aAbBcCzZ,但是手动处理成子文件夹的先reload

"""

g_allClasses={}

g_ReloadClassObjList=[] #需要热更新类
g_ReloadDataObjList=[] #需要热更新数据
g_ReloadClassDataObjList=[] #既热更新数据也热更新类
class Reload:
    RELOAD_CLASS=True
    def __init__(self,reloadClass=True,reloadData=False):
        if reloadData and reloadClass:
            g_ReloadClassDataObjList.append(weakref.ref(self))
        elif reloadClass:
            g_ReloadClassObjList.append(weakref.ref(self))
        elif reloadData:
            g_ReloadDataObjList.append(weakref.ref(self))
        pass


    def onReloadClass(self):
        pass

    def onReloadData(self):
        pass


def reloadAllModule():
    global g_allClasses
    g_allClasses={}
    #base cell common user_type文件夹内的所有py全部重载

    #reload common
    #得到cfunc.py文件前面的路径
    sb=KBEngine.getResFullPath("common/cfunc.py")
    sb=sb[:-8]
    ll=len(sb)
    _reloadComsAndBase(ll,"common")

    #reload server_common
    sb=KBEngine.getResFullPath("server_common/Duel.py")
    sb=sb[:-7]
    ll=len(sb)
    _reloadComsAndBase(ll,"server_common")

    #reload userType
    sb=KBEngine.getResFullPath("user_type/UserType.py")
    sb=sb[:-11]
    ll=len(sb)
    _reloadComsAndBase(ll,"user_type")

    if KBEngine.component=="baseapp":
        sb=KBEngine.getResFullPath("base/kbemain.py")
        sb=sb[:-10]
        ll=len(sb)
        _reloadComsAndBase(ll,"base")

    elif KBEngine.component=="cellapp":
        sb=KBEngine.getResFullPath("cell/kbemain.py")
        sb=sb[:-10]
        ll=len(sb)
        _reloadComsAndBase(ll,"cell")

    _reloadAllObjects()

#lllen是路径前段的长度
def _reloadComsAndBase(lllen,typeName):
    subL=[]
    l=[]
    for s in KBEngine.listPathRes(typeName,"py"):
        s=s[lllen:-3]
        s=s.replace('/','.')
        if s.find('.')!=-1:
            subL.append(s)
        else:
            l.append(s)

    #先重载a和c的,再重载实体
    reloadS="reload:"
    for s in subL:
        reloadS+=s+','
        mo=importlib.import_module(s)
        _reloadModule(mo)
    for s in l:
        reloadS+=s+','
        mo=importlib.import_module(s)
        _reloadModule(mo)
    INFO_MSG(reloadS)

"""
重载模块,然后把模块里面的需要重载的类全部加
"""
def _reloadModule(mo):
    if mo.__name__ in _blackList:
        return
    importlib.reload(mo)
    for name,Cls in inspect.getmembers(mo):
        if getattr(Cls,'RELOAD_CLASS',False):
            path=inspect.getsourcefile(Cls)
            g_allClasses[path+Cls.__name__]=Cls


def _reloadAllObjects():
    for i in range(len(g_ReloadClassObjList) - 1, -1, -1):
        obj=g_ReloadClassObjList[i]()
        if obj:
            n=inspect.getsourcefile(obj.__class__)+obj.__class__.__name__
            if n in g_allClasses:
                obj.__class__=g_allClasses[n]
                obj.onReloadClass()
            else:
                WARNING_MSG("not find Class "+n)
        else:
            del g_ReloadClassObjList[i]

    for i in range(len(g_ReloadClassDataObjList) - 1, -1, -1):
        obj=g_ReloadClassDataObjList[i]()
        if obj:
            n=inspect.getsourcefile(obj.__class__)+obj.__class__.__name__
            if n in g_allClasses:
                obj.__class__=g_allClasses[n]
                obj.onReloadClass()
            else:
                WARNING_MSG("not find Class "+n)
        else:
            del g_ReloadClassDataObjList[i]
    INFO_MSG("reload class obj ", len(g_ReloadClassObjList)+len(g_ReloadClassDataObjList))


def reloadAllObjectsData():
    for i in range(len(g_ReloadDataObjList) - 1, -1, -1):
        obj=g_ReloadDataObjList[i]()
        if obj:
            obj.onReloadData()
        else:
            del g_ReloadDataObjList[i]
    for i in range(len(g_ReloadClassDataObjList) - 1, -1, -1):
        obj=g_ReloadClassDataObjList[i]()
        if obj:
            obj.onReloadData()
        else:
            del g_ReloadClassDataObjList[i]
    #cell 报错原因不明
    print("reload data obj ", len(g_ReloadDataObjList)+len(g_ReloadClassDataObjList))


def cleanReloadObject():
    INFO_MSG("clean reload class ", len(g_ReloadClassObjList), len(g_ReloadDataObjList),len(g_ReloadClassDataObjList))
    for i in range(len(g_ReloadClassDataObjList) - 1, -1, -1):
        if not g_ReloadClassDataObjList[i]():
            del g_ReloadClassDataObjList[i]
    for i in range(len(g_ReloadClassObjList) - 1, -1, -1):
        if not g_ReloadClassObjList[i]():
            del g_ReloadClassObjList[i]
    for i in range(len(g_ReloadDataObjList) - 1, -1, -1):
        if not g_ReloadDataObjList[i]():
            del g_ReloadDataObjList[i]


g_allComponents={} # comName:comClass
def merge_g_allComponents():
    g_allComponents.clear()
    sb=KBEngine.getResFullPath("base/kbemain.py")
    sb=sb[:-10]
    ll=len(sb) #len need to del to get c/...

    coms=()
    nameBack='BA'
    if KBEngine.component=="baseapp":
        coms=KBEngine.listPathRes("base/c","py")
        nameBack='BA'
    if KBEngine.component=="cellapp":
        coms=KBEngine.listPathRes("cell/c","py")
        nameBack='CE'
    for s in coms:
        s=s[ll:-3]
        s=s.replace('/','.')
        mo=importlib.import_module(s)
        ClsName=s.split('.')[-1]
        Cls=getattr(mo,ClsName)
        g_allComponents[ClsName]=Cls
        # import KBEDebug
        # KBEDebug.ASSERT_MSG(ClsName[-2:]==nameBack,"%s not allow"%ClsName)
    # INFO_MSG("%s Components number= %d"%(KBEngine.component,len(g_allComponents)))


ALLOW_CONFLICT=["__annotations__","objMgrCE"]

def _checkEntityClassAttrConflict(EntityClass):
    nodeClass=EntityClass.__bases__[0]
    comList=EntityClass.__bases__[1:]
    for ComClass in comList:
        for attrname in ComClass.__dict__.keys():
            if attrname in ALLOW_CONFLICT:
                continue
            if attrname in dir(nodeClass):
                continue
            for ComClass2 in comList:
                if ComClass==ComClass2:
                    continue
                elif attrname in ComClass2.__dict__.keys():
                    ERROR_MSG("attr conflict Class=%s,Class2=%s,attrName=%s"%(ComClass.__name__,ComClass2.__name__,attrname))

def _checkEntityClassComponentLegal(EntityClass):
    #first Class must be
    firstName=EntityClass.__bases__[0].__name__
    import KBEDebug
    KBEDebug.ASSERT_MSG( firstName in ("NodeBA","NodeCE","SpaceNodeCE","SpaceNodeBA"),"first !=Node%s"%EntityClass.__name__)

def checkEntitiesAttrConflict():
    # noinspection PyUnresolvedReferences
    f=KBEngine.open("entities.xml",'r')
    string=f.read()
    f.close()
    entityXml=ET.fromstring(string)
    # entitiesNameList=[]
    for child in list(entityXml):
        # entitiesNameList.append(child.tag)
        try:
            mo=importlib.import_module(child.tag)
            EntityClass=getattr(mo,child.tag)
            _checkEntityClassComponentLegal(EntityClass)
            _checkEntityClassAttrConflict(EntityClass)
        except ImportError:
            continue
    print("%s Entities check Attr conflict complete!"%KBEngine.component)