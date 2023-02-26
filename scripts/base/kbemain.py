# -*- coding: utf-8 -*-
from KBEngine import *
import sys
import globalEventSystem
from util import *
import allcards



"""
"""
def onBaseAppReady(isBootstrap):
	"""
    KBEngine method.
    baseapp已经准备好了
    @param isBootstrap: 是否为第一个启动的baseapp
    @type isBootstrap: BOOL
    """
	INFO_MSG('onBaseAppReady: isBootstrap=%s, appID=%s, bootstrapGroupIndex=%s, bootstrapGlobalIndex=%s,debugVer=%d,engineVer=%d' % \
			 (isBootstrap, os.getenv("KBE_COMPONENTID"), os.getenv("KBE_BOOTIDX_GROUP"),
			  os.getenv("KBE_BOOTIDX_GLOBAL"),checkBase(),getEngineVersion()))

	if getEngineVersion()!=1:
		ERROR_MSG("please update your server engine at https://d1f8c6r0bq0fp8.cloudfront.net/vrduelserver.zip")
		return
	globalData["baseapp%d"%getCID()]=True

	reloadData()
	merge_g_allComponents()
	checkEntitiesAttrConflict()
	checkSceneJ()
	allcards.mergeAllCards()

	isUpdating=os.getenv('KBE_UPDATING',False)
	if isManagerBase():
		if not isWindows():
			setAppFlags(APP_FLAGS_NOT_PARTCIPATING_LOAD_BALANCING)
		if not isUpdating:
			createEntityLocally("Boot",{})



def onReadyForLogin(isBootstrap):
	"""
    KBEngine method.
    如果返回值大于等于1.0则初始化全部完成, 否则返回准备的进度值0.0~1.0。
    在此可以确保脚本层全部初始化完成之后才开放登录。
    @param isBootstrap: 是否为第一个启动的baseapp
    @type isBootstrap: BOOL
    """
	return 1.0

def onReadyForShutDown():
	"""
    功能说明：
    如果这个函数在脚本中有实现，当进程准备退出时，该回调函数被调用。

    可以通过该回调控制进程退出的时机。
    注意：该回调接口必须实现在入口模块(kbengine_defs.xml->entryScriptFile)中。


    返回：


    bool，如果返回True，则允许进入进程退出流程，返回其它值则进程会过一段时间后再次询问。
    """

	#这个函数在onBaseAppShutDown之后
	return True


def onBaseAppShutDown(state):
	"""
    KBEngine method.
    这个baseapp被关闭前的回调函数
    @param state: 0 : 在断开所有客户端之前
                  1 : 在将所有entity写入数据库之前
                  2 : 所有entity被写入数据库之后
    @type state: int
     state=0,然后在倒计时之后
    """

	#不会使用safekill了

	#如果在1的时候破坏物体会报错
	# if state==0:
	# 	globalEventSystem.fire_notifyGlobalServer("serverClose")
	# 	globalData["isShutdowning"]=True
	# elif state==1:
	# 	globalEventSystem.fire_onServerClose()

	INFO_MSG('onBaseAppShutDown: state=%i' % state)


def onInit(isReload):
	"""
    KBEngine method.
    当引擎启动后初始化完所有的脚本后这个接口被调用
    @param isReload: 是否是被重写加载脚本后触发的
    @type isReload: bool
    """
	INFO_MSG('onInit::isReload:%s' % isReload)


def onFini():
	"""
    KBEngine method.
    引擎正式关闭
    好像没实现
    """
	INFO_MSG('onFini()')


def onCellAppDeath(addr):
	"""
    KBEngine method.
    某个cellapp死亡
    """
	ERROR_MSG('onCellAppDeath: %s' % (str(addr)))

def onGlobalData(key, value):
	"""
    KBEngine method.
    globalData有改变
    """
	# DEBUG_MSG("onGlobalData %s"%key)
	globalEventSystem.onGlobalEventData(key, value)

def onGlobalDataDel(key):
	"""
    KBEngine method.
    globalData有删除
    """
	# onUtilGlobalDataDel(key)
	pass

def onBaseAppData(key, value):
	"""
    KBEngine method.
    globalBases有改变
    """
	# onUtilBaseData(key,value)
	pass


def onBaseAppDataDel(key):
	"""
    KBEngine method.
    globalBases有删除
    """
	# onUtilBaseDataDel(key)
	pass


def onLoseChargeCB(ordersID, dbid, success, datas):
	"""
    KBEngine method.
    有一个不明订单被处理， 可能是超时导致记录被billing
    清除， 而又收到第三方充值的处理回调
    """
	DEBUG_MSG('onLoseChargeCB: ordersID=%s, dbid=%i, success=%i, datas=%s' % \
			  (ordersID, dbid, success, datas))

#自动加载的实体,在里面创建
#不好用,老是创建多个
# def onAutoLoadEntityCreate( entityType, dbID ):
#     if getCID()==1:
#         for managerName in managerList:
#             if entityType==managerName:
#                 if entityType in globalData:
#                     ERROR_MSG("has Manager",entityType)
#                     return
#                 INFO_MSG("restore manager",entityType)
#                 createEntityFromDBID(entityType,dbID)
