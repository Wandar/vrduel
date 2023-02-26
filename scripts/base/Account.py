# -*- coding: utf-8 -*-
from c.AccountBA import AccountBA
from c.NodeBA import NodeBA

class Account(NodeBA,AccountBA):
	OVERRIDE_LOSE_CELL=True
	pass
