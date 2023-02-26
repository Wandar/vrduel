# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2017 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2017/8/27 3:29

from KBEngine import *

from c.NodeBA import NodeBA
from c.gamemanager.AccountManagerBA import AccountManagerBA
from c.gamemanager.GameManagerBA import GameManagerBA
from c.gamemanager.SpaceManagerBA import SpaceManagerBA
from c.gamemanager.DataLoaderManagerBA import DataLoaderManagerBA
from c.gamemanager.VoiceManagerBA import VoiceManagerBA


class GameManager(NodeBA,GameManagerBA, SpaceManagerBA,AccountManagerBA,DataLoaderManagerBA,VoiceManagerBA):
    pass




