# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2017 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2017/9/12 1:27

from KBEngine import *

from c.ComponentBA import ComponentBA
from util import *


class ProxyBA(Proxy, ComponentBA):
    def onLoad(self):
        pass

    #没有cell
    def onClientEnabled(self):
        pass

    def onGiveClientToFailure(self):
        pass

    def onClientGetCell( self ):
        pass

    def onStreamComplete(self,id, success ):
        pass

    def onLogOnAttempt(self, ip, port, password):
        INFO_MSG("onLogOnAttempt return accept")
        return LOG_ON_ACCEPT
        pass


    #只有在强制退出才会触发,giveClientTo不会触发
    def onClientDeath(self):
        pass


    def onDestroy( self ):
        pass

