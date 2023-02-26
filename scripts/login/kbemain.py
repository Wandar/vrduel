# -*- coding: utf-8 -*-
import sys
from util import *


try:
	sys.path.append(os.getenv("curpath")+"/sec")
	import loginfunc
except:
	pass


def onLoginAppReady():
	INFO_MSG('onLoginAppReady: bootstrapGroupIndex=%s, bootstrapGlobalIndex=%s' % \
	 (os.getenv("KBE_BOOTIDX_GROUP"), os.getenv("KBE_BOOTIDX_GLOBAL")))

def onLoginAppReadyDebug():
	INFO_MSG('onLoginAppReadyDebug: bootstrapGroupIndex=%s, bootstrapGlobalIndex=%s' % \
			 (os.getenv("KBE_BOOTIDX_GROUP"), os.getenv("KBE_BOOTIDX_GLOBAL")))

def onTick(timerID):
	INFO_MSG('onTick()')

def onLoginAppShutDown():
	INFO_MSG('onLoginAppShutDown()')


def onRequestLogin(loginName, password, clientType, datas):
	return loginfunc.onRequestLogin(loginName, password, clientType, datas)


def onRequestCreateAccount(accountName, password, datas):
	return loginfunc.onRequestCreateAccount(accountName, password, datas)


def onLoseLogin(loginName):
	pass

def onLoginCallbackFromDB(loginName, accountName, errorno, datas):
	INFO_MSG('onLoginCallbackFromDB() loginName=%s, accountName=%s, errorno=%s' % (loginName, accountName, errorno))



def onCreateAccountCallbackFromDB(accountName, errorno, datas):
	INFO_MSG('onCreateAccountCallbackFromDB() accountName=%s, errorno=%s' % (accountName, errorno))


# def onGlobalData(key, value):
# 	INFO_MSG("onGlobalData %s"%key)
#
# def onGlobalDataDel(key):
# 	INFO_MSG('onDelGlobalData: %s' % key)