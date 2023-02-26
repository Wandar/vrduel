# -*- coding: utf-8 -*-
#    Copyright (C) 2016-2017 __COMPANY_NAME
#    All rights reserved
#
#    created by zone at 2017/8/27 3:29
from __future__ import annotations
from KBEngine import *

from c.NodeBA import NodeBA
from c.AvatarBA import AvatarBA

class Avatar(NodeBA,AvatarBA):
        OVERRIDE_LOSE_CELL=True
