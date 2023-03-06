# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2018 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2018-04-27 19:43

from KBEngine import *
import urllib.parse

from globalEventSystem import *
from util import *
from c.ComponentBA import ComponentBA
import sys

from tornado import httpserver, ioloop, websocket, web, gen
from tornado.websocket import websocket_connect

sys.path.append(os.getenv("KBE_ROOT") + '/kbe/res/scripts/lib')
TORNADO_MANAGER_PORT=32564
try:
    sys.path.append(os.getenv("curpath") + "/sec")
    import secfile
    TORNADO_MANAGER_PORT=secfile.TORNADO_MANAGER_PORT
except:
    pass


STATE_NONE = 0
STATE_CONNECTING = 1
STATE_CONNECTED = 2
STATE_SENDING = 3

VERIFIER_PORTS = [21000, 21001, 21002, 21003, 21004]


class BootBA(ComponentBA):
    server = None
    verifierClients = None
    fpClient = None
    muIapApp = None
    checkBuyOrders = None

    keepAliveCnt = 0

    def onLoad(self):
        globalData["Boot"] = self
        globalData["tornadoBase"] = self

        self.verifierClients = []
        self.checkBuyOrders = {}

        #mu iap
        # self.initMuIap()

        INFO_MSG("start websocket server")
        #tornado control funcs
        ws_app = Application()
        server = httpserver.HTTPServer(ws_app)
        self.server = server
        server.listen(TORNADO_MANAGER_PORT)
        self.setInterval(0.1, 0, self.onTimerTornado)

        self.setInterval(1000, 1000, self.onTimerCleanReloadPool)
        # self.setInterval(50,100,self.onTimerCleanGarbages)

        # self.setInterval(1,1,self.onTimerCheckCheckBuy)
        # self.setInterval(15,3,self.onTimerSendKeepAlive)

        self.startGameManager()

    def onTimerTornado(self, tid):
        t1 = time.time()
        ioloop.IOLoop.current().start()
        usedTime = time.time() - t1
        if usedTime > 1:
            ERROR_MSG("tornado used time=%f" % usedTime)
        self.setInterval(0.1, 0, self.onTimerTornado)

    def onTimerCleanReloadPool(self, tid):
        # INFO_MSG("fire_cleanReloadObject")
        if cvec3Zero.x != 0 or cvec3Zero.y != 0 or cvec3Zero.z != 0:
            ERROR_MSG("cvec3Zero !=0")
        fire_cleanReloadObject()

    def onTimerCleanGarbages(self, tid):
        fire_cleanGarbages()

    def startGameManager(self):
        if isDebugVer():
            self._onCreateManagerCB(None, None, None)
        else:
            createEntityFromDBID("GameManager", 1, self._onCreateManagerCB)

    def _onCreateManagerCB(self, baseRef, databaseID, wasActive):
        """
        如果操作成功，baseRef会是一个call或者是新创建的Base实体的直接引用，databaseID会是实体的数据库ID，无论该实体是否已经激活
        wasActive都会有所指示，如果wasActive是True则baseRef是已经存在的实体的引用(已经从数据库检出)。如果操作失败这三个参数的值，baseRef将会是None，databaseID将会是0，wasActive将会是False。
        失败最常见的原因是实体在数据库里不存在，但偶尔也会出现其它错误比如说超时或者是分配ID失败。
        """
        INFO_MSG("start success")
        if baseRef == None:
            INFO_MSG("create new gamemanager")
            createEntityLocally("GameManager", {})

    #p
    def reset(self):
        INFO_MSG("destroy GameManager")
        getGameManager().tryDestroy()
        self.setInterval(5, 0, self._onTimerReset)

    #p
    def destroyGameManager(self):
        getGameManager().tryDestroy()

    def _onTimerReset(self, tid):
        fire_reloadScript()
        self.startGameManager()
        INFO_MSG("restart GameManager")

    verifierCnt = 0
    verifierErrCnt = 0

    def reinitVerifierClients(self):
        if len(self.verifierClients):
            for v in self.verifierClients:
                v.closeConnect()
        self.verifierCnt = 0
        self.verifierErrCnt = 0
        self.verifierClients = []
        for i in range(len(VERIFIER_PORTS)):
            port = VERIFIER_PORTS[i]
            self.verifierClients.append(VerifierClient(port, i))

    def chooseVerifierClient(self):
        self.verifierCnt += 1
        if self.verifierCnt >= len(self.verifierClients):
            self.verifierCnt = 0
        return self.verifierClients[self.verifierCnt]

    #p UINT8
    def onVerifierDisconnect(self, queueID):
        #可能导致pool越来越大
        pool = self.verifierClients[queueID].messagePool
        self.verifierClients[queueID].closeConnect()
        self.verifierClients[queueID] = VerifierClient(VERIFIER_PORTS[queueID], queueID)
        ERROR_MSG("onVerifierDisconnect ", queueID, len(pool))

    def checkBase(self):
        if not hasattr(self.__class__, "setInterval"):
            sys.exit()

    #p CALL STRING STRING
    def requestCheckBuy(self, accountMail, myOrderID, data):
        INFO_MSG('requestCheckBuy ', myOrderID)

        if myOrderID in self.checkBuyOrders:
            WARNING_MSG("check same order ", myOrderID)
            if time.time() - self.checkBuyOrders[myOrderID]['time'] < 2:  #2秒内第二个
                return

        #找一个client发送请求验证信息
        self.checkBuyOrders[myOrderID] = {
            "mail": accountMail,
            "data": data,
            "time": time.time(),
            "resend": 0,
            'sendvID': 0
        }
        vclient = self.chooseVerifierClient()
        vclient.reqSend(data)
        self.checkBuyOrders[myOrderID]['sendvID'] = self.verifierCnt

    #p STRING
    def onCheckBuyRecv(self, data):
        j = json.loads(data)
        myID = j['myOrderID']
        INFO_MSG("onCheckBuyRecv ", myID)
        if myID not in self.checkBuyOrders:
            WARNING_MSG('myID not in self.checkBuyOrders', myID)
            return

        resend = self.checkBuyOrders[myID]['resend']
        if resend > 0:
            INFO_MSG('onCheckBuyRecv myOrder=%s resend=%d' % (myID, resend))
        mail = self.checkBuyOrders[myID]['mail']  #type:AccountBA
        mail.onRequestCheckBuy(myID, data)
        if j['success'] != ERR_REQUEST_TIMEOUT or j['success'] != UNEXPECTED_FAIL:
            del self.checkBuyOrders[myID]

    def onTimerCheckCheckBuy(self, tid):
        delOrder = []
        for myOrderID, tempj in self.checkBuyOrders.items():
            if time.time() - tempj['time'] > 10:  #resend
                INFO_MSG("too long time checkBuy resend id=%s client=%d" % (myOrderID, tempj['sendvID']))
                self.verifierErrCnt += 1
                vclient = self.chooseVerifierClient()
                vclient.reqSend(tempj['data'])
                tempj['sendvID'] = self.verifierCnt
                tempj['time'] = time.time()
                tempj['resend'] += 1
                if tempj['resend'] > 5:
                    ERROR_MSG("too much checkBuy resend ", tempj['data'])
                    delOrder.append(myOrderID)
        for a in delOrder:
            del self.checkBuyOrders[a]

    def onTimerSendKeepAlive(self, tid):
        self.keepAliveCnt += 1
        if self.keepAliveCnt >= 5:
            self.keepAliveCnt = 0
        if self.keepAliveCnt < len(self.verifierClients):
            self.verifierClients[self.keepAliveCnt].keep_alive()

    _closingCnt = 5
    _closingTid = 0

    def closingNotify(self):
        self._closingCnt = 5
        if self._closingTid:
            self.delInterval(self._closingTid)
        self._closingTid = self.setInterval(60, 60, self.onTimerClosing)

    def onTimerClosing(self, tid):
        fire_closingNotify(self._closingCnt)
        self._closingCnt -= 1
        if self._closingCnt == 0:
            self.delInterval(self._closingTid)
            self._closingTid = 0

    def onDestroy(self):
        del globalData["Boot"]
        self.server.stop()


try:
    class VerifierClient(object):
        queueID = 0
        ws = None
        messagePool = []
        port = 0
        keepaliveTime = 0
        isDestroyed = False

        def __init__(self, port, queuID, messageP=None):
            self.ws = None
            self.state = STATE_NONE
            self.port = port
            self.queueID = queuID
            if messageP:
                self.messagePool = messageP
            self.tryConnect()

        @gen.coroutine
        def tryConnect(self):
            if self.state == STATE_CONNECTING:
                return
            self.ws = None
            url = "ws://%s:%s" % ('127.0.0.1', self.port)
            INFO_MSG("try connect", url)
            try:
                self.state = STATE_CONNECTING
                self.ws = yield websocket_connect(url, connect_timeout=10)
            except Exception:
                ERROR_MSG("connection error ", url)
                self.state = STATE_NONE
            else:
                self.state = STATE_CONNECTED
                for message in self.messagePool:
                    self.ws.write_message(message)
                    self.ws.read_message(self.onRecvMessage)
                self.messagePool = []

            if self.isDestroyed:
                self.closeConnect()

        def closeConnect(self):
            if self.ws:
                self.ws.close()
            self.isDestroyed = True

        """
        返回
        {
            "myOrderID":""
            "productID":""
            "success":SUCCESS
        }
    
        """

        def onRecvMessage(self, sb):
            if self.isDestroyed:
                return
            s = sb.result()
            if s == 'keepalive':
                self.keepaliveTime = 0
                pass
            else:
                globalData['tornadoBase'].onCheckBuyRecv(s)

        def reqSend(self, message):
            if self.isDestroyed:
                return
            if message != 'keepalive':
                DEBUG_MSG("reqSend", message)
            if not self.ws:
                self.messagePool.append(message)
                self.tryConnect()
            else:
                try:
                    self.ws.write_message(message)
                    self.ws.read_message(self.onRecvMessage)
                except:
                    self.messagePool.append(message)
                    self.tryConnect()

        def keep_alive(self):
            if self.isDestroyed:
                return
            #必须加这个,因为出现过卡死的情况
            if self.keepaliveTime:
                globalData['tornadoBase'].onVerifierDisconnect(self.queueID)
                return
            self.keepaliveTime = time.time()
            self.reqSend("keepalive")
except:
    pass




class WebSocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        pass

    def on_message(self, message):
        if not isDebugVer():
            if message[:20] != secfile.ORDER_PASSWORD:
                self.write_message(u'wrongpass')
                self.close()
                return
            message = message[20:]

        if message == ORDER_RELOAD_SCRIPT:  #hot reload scripts
            fire_reloadScript()
            self.write_message(u'ok')
        elif message == ORDER_RELOAD_DATA:  #hot reload data
            fire_reloadData()
            self.write_message(u'ok')
        elif message == ORDER_RESET:  #reset all
            globalData["Boot"].reset()
            self.write_message(u'ok')
        elif message == ORDER_GET_NUM:  #get accounts num
            num = getAccountManagerBA().getAccountNum()
            self.write_message(u'num=%d ok' % num)
        elif message == ORDER_SAVE_DATA_AND_END:  #save all accounts data and close server
            fire_onServerClose()
            getGameManager().saveAllAccountsData(self)
        elif message == ORDER_CLOSING_NOTIFY:  #notify closing server count down
            globalData["Boot"].closingNotify()
            self.write_message(u'closing notify ok')
        elif ORDER_NOTIFY in message:  #notify message
            s = message[24:]
            if s:
                fire_notifyGlobalServerWord(s)
            self.write_message(u'ok')
        else:
            self.write_message(u'unknowok')

    def on_close(self):
        pass


class Application(web.Application):
    def __init__(self):
        handlers = [
            (r'/', WebSocketHandler)
        ]
        settings = {"template_path": "."}
        web.Application.__init__(self, handlers, **settings)
