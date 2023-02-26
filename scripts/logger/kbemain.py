# -*- coding: utf-8 -*-
import os
from KBEngine import *
from util import *
if 0:from logger.KBEngine import *
import smtpUtil

"""
logger进程主要处理KBEngine服务端的日志保存工作。

开机发送启动成功,收到错误发送邮件
"""
sendWarnErrorBuffer=[]
errorBuffer=[]
errorFlag=False
warningCnt=0

isReadingIniting=True
readingInitingLog=[]
g_isShuttingDown=False #是否正在手动关服
g_isRebooting=False #是否正在因为crash而重启
g_lastSendErrorTime=0

specialEmailBuffer=[]

def onLoggerAppReady():
	"""
    KBEngine method.
    logger已经准备好了
    """
	INFO_MSG('onLoggerAppReady: bootstrapGroupIndex=%s, bootstrapGlobalIndex=%s' % \
			 (os.getenv("KBE_BOOTIDX_GROUP"), os.getenv("KBE_BOOTIDX_GLOBAL")))
	addTimer(0.5,0, onTimerStartSend)
	addTimer(1,0,onTimerSendMail)
	addTimer(60,0,sendInitedLog)

def onTimerStartSend(a=None):
	serverName=os.getenv("SERVER_NAME","NoName")
	i=3
	while i:
		if smtpUtil.sendMailSSL(serverName+" logger up","logger up\nlogger up\nlogger up\n"):
			break
		i-=1

def sendInitedLog(a=None):
	serverName=os.getenv("SERVER_NAME","NoName")
	allMsg=""
	for i in range(len(readingInitingLog)-1,-1,-1):
		s=readingInitingLog[i]
		allMsg+=s+'\n'
	i=3
	while i:
		if smtpUtil.sendMailSSL(serverName+" initedLog ",allMsg):
			break
		i-=1
	global isReadingIniting
	isReadingIniting=False

def sendCrash():
	serverName=os.getenv("SERVER_NAME","NoName")
	title='CRASH '+serverName
	global errorFlag
	global warningCnt

	allMsg=""
	for s in sendWarnErrorBuffer:
		allMsg+=s+'\n'

	#发两次
	if smtpUtil.sendMailSSL(title, allMsg):
		INFO_MSG('send crash ok ',title)
	else:
		smtpUtil.sendMailSSL(title, allMsg)
	errorFlag=False
	sendWarnErrorBuffer.clear()
	warningCnt=0


def onTimerSendMail(a=None):
	global g_lastSendErrorTime
	if time.time()-g_lastSendErrorTime>60: #每分钟发一次error
		title=""
		serverName=os.getenv("SERVER_NAME","NoName")
		global errorFlag
		global warningCnt
		if errorFlag:
			title="error "+serverName+' errorX'+str(len(errorBuffer))
		elif warningCnt>1000:
			title="warn "+serverName

		if title:
			allMsg=""
			for s in errorBuffer:
				allMsg+=s+'\n'
			allMsg+='--------------------------ALL----------------------------\n'
			for s in sendWarnErrorBuffer:
				allMsg+=s+'\n'
			allMsg+='--------------------------KNOWN--------------------------\n'
			for s,num in g_KNOWN_ERRORS.items():
				allMsg+=('\n     num='+str(num)+'  '+s+'\n')
			allMsg+='---KNOWN_WARN---\n'
			for s,num in g_KNOWN_WARNINGS.items():
				allMsg+=('\n     num='+str(num)+'  '+s+'\n')
			if len(allMsg)>1000000:
				serverName=os.getenv("SERVER_NAME","NoName")
				title=serverName+'msg too long'
				allMsg='too long'
			g_lastSendErrorTime=time.time()
			if smtpUtil.sendMailSSL(title, allMsg):
				errorFlag=False
				sendWarnErrorBuffer.clear()
				errorBuffer.clear()
				clearKnown()
				warningCnt=0


	for i in range(len(specialEmailBuffer)-1,-1,-1):
		#防卡死这里重发一次
		n=2
		while n:
			if sendSpecialEmail(specialEmailBuffer[i]):
				break
			n-=1
		del specialEmailBuffer[i]

	addTimer(1,0,onTimerSendMail)


def clearKnown():
	for s in g_KNOWN_ERRORS:
		g_KNOWN_ERRORS[s]=0
	for s in g_KNOWN_WARNINGS:
		g_KNOWN_WARNINGS[s]=0


def onLoggerAppShutDown():
	"""
    KBEngine method.
    这个logger被关闭前的回调函数
    """
	INFO_MSG('onLoggerAppShutDown()')
	global g_isShuttingDown
	g_isShuttingDown=True


def onReadyForShutDown():
	"""
    KBEngine method.
    logger询问脚本层：我要shutdown了，你（脚本）是否准备好了？
    如果返回True，则logger会进入shutdown的流程，其它值会使得logger在过一段时间后再次询问。
    用户可以在收到消息时进行脚本层的数据清理工作，以让脚本层的工作成果不会因为shutdown而丢失。
    """
	INFO_MSG('onReadyForShutDown()')
	global g_isShuttingDown
	g_isShuttingDown=True

	return True


def onLogWrote(logData):
	"""
    KBEngine method.
    logger写入了一条日志后的回调，
    有需要的用户可以在此处把日志写入到其它的地方（如数据库）
    @param logData: bytes
    """


	logData=bytes.decode(logData) # WARNING 8个  S_WARN也是8个   ERROR

	if isReadingIniting:
		readingInitingLog.append(logData)

	head=logData[0:8]
	# if 'ServerApp::reqCloseServer' in logData:
	#     global g_isRebooting
	#     g_isRebooting=True

	if head=="   S_ERR" or head=="   ERROR":
		checkIsCrash(logData)
		if isAddIgnoredError(logData):
			pass
		elif LOGGER_EMAIL in logData: #这是特殊邮件
			specialEmailBuffer.append(logData)
		else:
			sendWarnErrorBuffer.append(logData)
			errorBuffer.append(logData)
			ERROR_MSG(logData)
			global errorFlag
			errorFlag=True
	elif head==" WARNING" or head=="  S_WARN":
		if isAddIgnoredWarn(logData):
			pass
		else:
			# WARNING_MSG(logData)
			sendWarnErrorBuffer.append(logData)
			global warningCnt
			warningCnt+=1



def sendSpecialEmail(logData):
	if EMAIL_TITLE_END not in logData:
		return True

	e=logData.find(LOGGER_EMAIL)
	logData=logData[e:]
	s=logData.replace(LOGGER_EMAIL,"")

	e=s.find(EMAIL_TITLE_END)
	biaoti=s[:e]
	neirong=s[e:].replace(EMAIL_TITLE_END,"")
	return smtpUtil.sendMailSSL(biaoti,neirong)

def checkIsCrash(logData):
	if g_isShuttingDown:
		return False
	global g_isRebooting
	if isWindows():
		return False
	#Components::removeComponentByChannel: baseapp : 3, Abnormal exit!

	crashType=0
	if 'Abnormal exit' in logData:
		if 'Components::removeComponentByChannel: cellapp' in logData:
			crashType=1
		else:
			crashType=2

	if not crashType:
		return False

	#cell 崩掉后不要重启
	if crashType==1:
		sendWarnErrorBuffer.append(logData)
		sendCrash()
		return True

	elif crashType==2:
		sendWarnErrorBuffer.append(logData)
		sendCrash()
		if g_isRebooting:
			return True
		g_isRebooting=True
		addTimer(1,0,onTimerReboot)
		return True

def onTimerReboot(a=None):
	debug='release'
	shFile='start_server.sh'
	os.system('cd sec;fab -f fabfileToSlave startServer:"%s"'%debug)
	os.system('cd sec;sh %s'%shFile)


def isAddIgnoredWarn(logData):
	for s in g_KNOWN_WARNINGS:
		if s in logData:
			g_KNOWN_WARNINGS[s]+=1
			return True
	return False

def isAddIgnoredError(logData):
	for s in g_KNOWN_ERRORS:
		if s in logData:
			g_KNOWN_ERRORS[s]+=1
			return True
	return False

"""
被注释掉的错误
Channel::processPackets({}): channel[{:p}] is condemn.

"""

g_KNOWN_ERRORS={
	'KCPPacketSender::ikcp_send: send error! currPacketSize=':0,
	'Exception occurred: REASON_CHANNEL_LOST':0,
	'Channel::processPackets(':0,#删除这条
	'Baseapp::onUpdateDataFromClient: invalid data, size(':0,
	'TCPPacketSender::processSend(external): Exception occurred: REASON_CLIENT_DISCONNECTED':0,
	'PacketReader::processMessages: not found msgID':0,#经常会收到不明ip的请求
	'Account::onClientDeath:':0,
	'EndPoint::setupSSL:':0,
	'Attempted to get in MemoryStream':0,
	# 'UDPPacketSender::processSend(external:0, sendfailCount(10) >= 10): Exception occurred: REASON_RESOURCE_UNAVAILABLE':0,  #出错极多
	'WebSocketPacketFilter::recv: frame error!':0,
	'Exception occurred: REASON_WEBSOCKET_ERROR':0,
	'HTTPCBHandler:handleInputNotification: recv error, newclient = ':0,
}


g_KNOWN_WARNINGS={
	'Channel::processPackets(':0,
	#"WebSocketPacketFilter::send: no free space, buffer added":0, 被注释掉了
	"Baseapp::onRemoteCallCellMethodFromClient:":0,
	'Baseapp::onUpdateDataFromClient: Account':0,
}


# INFO_MSG(logData)
#得到本机名字和ip地址
# hostname=socket.gethostname()
# ip=socket.gethostbyname(hostname)
# INFO_MSG(logData)

