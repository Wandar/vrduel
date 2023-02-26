# -*- coding: utf-8 -*-
from KBEngine import *

from c.space.SpaceBA import SpaceBA
from c.space.SpaceNodeBA import SpaceNodeBA
from util import *


class Space(SpaceNodeBA, SpaceBA):
    OVERRIDE_LOSE_CELL=True
    def __init__(self):
        SpaceNodeBA.__init__(self)

    def onDestroy( self ):
        SpaceNodeBA.onDestroy(self)







