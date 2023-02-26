# -*- coding: utf-8 -*-
import json
import os
import sys
import time

import KBEngine
from KBEDebug import *
from ServerConstants import *
from Constants import *
if 0:
	import interfaces.KBEngine

sys.path.append(os.getenv("KBE_ROOT")+'/kbe/res/scripts/lib')


fpclient=None
s_fpclient=None
try:
	sys.path.append(os.getenv("curpath")+"/sec")
	from script import fpclient
	from tornado import ioloop
except:
	pass

s_message=[]

def onTornadoIOLoop(timerID):
	"""
    """
	KBEngine.delTimer( timerID )
	ioloop.IOLoop.current().start()
	KBEngine.addTimer(0.1, 0, onTornadoIOLoop)

def onTimerWatchDog(timerID):
	global s_fpclient
	if time.time()-s_fpclient.lastRecvTime>20:
		s_fpclient.closeConnect()
		messagePool=s_fpclient.messagePool
		if len(messagePool)>20:
			messagePool=[]#如果积攒的数据太多就清空
		s_fpclient=fpclient.FPClient(messagePool)
		ERROR_MSG("reset fpclient")


def onTimerSendFPData(timerID):
	s_fpclient.reqSend()

g_isDebugVer=False
def onInterfaceAppReady():
	"""
	KBEngine method.
	interfaces已经准备好了
	"""
	INFO_MSG('onInterfaceAppReady: bootstrapGroupIndex=%s, bootstrapGlobalIndex=%s' % \
	 (os.getenv("KBE_BOOTIDX_GROUP"), os.getenv("KBE_BOOTIDX_GLOBAL")))

	# if fpclient:
	# 	KBEngine.addTimer(0.1, 0, onTornadoIOLoop)
	# 	global s_fpclient
	# 	s_fpclient=fpclient.FPClient()
	# 	KBEngine.addTimer(0.2,0.2,onTimerSendFPData)
	# 	KBEngine.addTimer(1,1,onTimerWatchDog)

	#KBEngine.addTimer(0.01, 1.0, onTick)

def onInterfaceAppReadyDebug():
	INFO_MSG('onInterfaceAppReady: bootstrapGroupIndex=%s, bootstrapGlobalIndex=%s' % \
			 (os.getenv("KBE_BOOTIDX_GROUP"), os.getenv("KBE_BOOTIDX_GLOBAL")))
	global g_isDebugVer
	g_isDebugVer=True

def onTick(timerID):
	"""
	"""
	INFO_MSG('onTick()')

	# 测试数据库查询
	# KBEngine.executeRawDatabaseCommand("select * from kbe_accountinfos limit 3;", onSqlCallback)
	# KBEngine.urlopen("https://www.baidu.com", onHttpCallback)

def onInterfaceAppShutDown():
	"""
	KBEngine method.
	这个interfaces被关闭前的回调函数
	"""
	INFO_MSG('onInterfaceAppShutDown()')

def onRequestCreateAccount(registerName, password, datas):
	"""
	KBEngine method.
	请求创建账号回调
	@param registerName: 客户端请求时所提交的名称
	@type  registerName: string
	
	@param password: 密码
	@type  password: string
	
	@param datas: 客户端请求时所附带的数据，可将数据转发第三方平台
	@type  datas: bytes
	"""
	INFO_MSG('onRequestCreateAccount: registerName=%s' % (registerName))
	
	commitName = registerName
	
	# 默认账号名就是提交时的名
	realAccountName = commitName 
	
	# 此处可通过http等手段将请求提交至第三方平台，平台返回的数据也可放入datas
	# datas将会回调至客户端
	# 如果使用http访问，因为interfaces是单线程的，同步http访问容易卡住主线程，建议使用
	# KBEngine.urlopen("https://www.baidu.com",onHttpCallback)异步访问。也可以结合异步socket的方式与平台交互（参考Poller.py)。
	datasStr=bytes.decode(datas)
	DEBUG_MSG('onRequestCreateAccount: registerName=%s passwd=%s datas=%s' % (registerName,password,datasStr))
	KBEngine.createAccountResponse(registerName, registerName, datas, SERVER_SUCCESS)

	# if datasStr=='bots':
	# 	KBEngine.createAccountResponse(registerName, registerName, datas, SERVER_SUCCESS)
	# 	return
	#
	# datajson=json.loads(datasStr)
	# loginType=datajson["type"]
	# if loginType=="fastplayio":
	# 	s_fpclient.onRequestCreateAccount(registerName, password, datas)
	# 	pass
	# elif loginType=="guest":
	# 	# if _checkGuestAccountLegal(registerName):
	# 	KBEngine.createAccountResponse(registerName, registerName, datas, SERVER_SUCCESS)
	# 	# else:#illegal
	# 	#     createAccountResponse(registerName, registerName, datas, SERVER_ERR_ACCOUNT_CREATE_FAILED)
	# #是普通注册
	# elif loginType=='normal':
	# 	createAccountResponse(registerName, registerName, datas, SERVER_SUCCESS)


def onRequestAccountLogin(loginName, password, datas):
	"""
	KBEngine method.
	请求登陆账号回调
	@param loginName: 客户端请求时所提交的名称
	@type  loginName: string
	
	@param password: 密码
	@type  password: string
	
	@param datas: 客户端请求时所附带的数据，可将数据转发第三方平台
	@type  datas: bytes
	"""
	INFO_MSG('onRequestAccountLogin: registerName=%s' % (loginName))
	
	commitName = loginName
	
	# 默认账号名就是提交时的名
	realAccountName = commitName 
	
	# 此处可通过http等手段将请求提交至第三方平台，平台返回的数据也可放入datas
	# datas将会回调至客户端
	# 如果使用http访问，因为interfaces是单线程的，同步http访问容易卡住主线程，建议使用
	# KBEngine.urlopen("https://www.baidu.com",onHttpCallback)异步访问。也可以结合异步socket的方式与平台交互（参考Poller.py)。
	
	# 如果返回码为KBEngine.SERVER_ERR_LOCAL_PROCESSING则表示验证登陆成功，但dbmgr需要检查账号密码，KBEngine.SERVER_SUCCESS则无需再检查密码
	retcode=SERVER_ERR_LOCAL_PROCESSING
	if g_isDebugVer:
		retcode=SERVER_SUCCESS

	KBEngine.accountLoginResponse(commitName, realAccountName, datas, retcode)
	
def onRequestCharge(ordersID, entityDBID, datas):
	"""
	KBEngine method.
	请求计费回调
	@param ordersID: 订单的ID
	@type  ordersID: uint64
	
	@param entityDBID: 提交订单的实体DBID
	@type  entityDBID: uint64
	
	@param datas: 客户端请求时所附带的数据，可将数据转发第三方平台
	@type  datas: bytes
	"""

	#no use
	ERROR_MSG('onRequestCharge: entityDBID=%s, entityDBID=%s' % (ordersID, entityDBID))
	KBEngine.chargeResponse(ordersID, datas, KBEngine.SERVER_SUCCESS)


def onSqlCallback(result, rows, insertid, error):
	DEBUG_MSG('onSqlCallback: result=%s, rows=%s, insertid=%s, error=%s' % (str(result), str(rows), str(insertid), str(error)))

def onHttpCallback(httpcode, data, headers, success, url):
	DEBUG_MSG('onHttpCallback: httpcode=%i, data=%s, headers=%s, success=%s, url=%s' % (httpcode, data, headers, str(success), url))




