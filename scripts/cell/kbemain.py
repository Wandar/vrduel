# -*- coding: utf-8 -*-
import KBEngine
import sys
import globalEventSystem
from util import *
from dataLoader import reloadData
import allcards





def onInit(isReload):
	DEBUG_MSG('onInit::isReload:%s' % isReload)
	if not isReload:
		KBEngine.globalData["cellapp%d"%getCID()]=True
		reloadData()
		merge_g_allComponents()
		checkEntitiesAttrConflict()
		allcards.mergeAllCards()
		INFO_MSG("start success")


def onGlobalData(key, value):
	"""
	KBEngine method.
	globalData改变 
	"""
	# DEBUG_MSG("onGlobalData %s"%key)
	globalEventSystem.onGlobalEventData(key, value)

def onGlobalDataDel(key):
	"""
	KBEngine method.
	globalData删除 
	"""
	DEBUG_MSG('onDelGlobalData: %s' % key)

def onCellAppData(key, value):
	"""
	KBEngine method.
	"""
	DEBUG_MSG('onCellAppData: %s' % key)
	
def onCellAppDataDel(key):
	"""
	KBEngine method.
	"""
	DEBUG_MSG('onCellAppDataDel: %s' % key)
	
def onSpaceData( spaceID, key, value ):
	"""
	KBEngine method.
	spaceData改变
	@spaceID:  数据被设置在这个spaceID的space中.  
	@key:  被设置的key.  
	@value:  被设置的值， 如果值被删除则为None.  
	"""
	DEBUG_MSG('onSpaceData: spaceID=%s, key=%s, value=%s.' % (spaceID, key, value))
	
def onSpaceGeometryLoaded(spaceID, mapping):
	"""
	KBEngine method.
	space 某部分或所有chunk等数据加载完毕
	具体哪部分需要由cell负责的范围决定
	"""
	DEBUG_MSG('onSpaceGeometryLoaded: spaceID=%s, mapping=%s.' % (spaceID, mapping))
	
def onAllSpaceGeometryLoaded(spaceID, isBootstrap, mapping):
	"""
	KBEngine method.
	space 某部分或所有chunk等数据加载完毕
	具体哪部分需要由cell负责的范围决定
	"""
	DEBUG_MSG('onAllSpaceGeometryLoaded: spaceID=%s, isBootstrap=%i, mapping=%s.' % (spaceID, isBootstrap, mapping))
	

