# -*- coding: utf-8 -*-
from util import *
from annos import *
class EventSystem:
    interestedEntities=None
    beInterestedEntities=None #被感兴趣
    interestedEvents=None #messageName:func
    #只有需要感兴趣才能触发的事件在这里面
    def __init__(self):
        self.interestedEntities={}
        self.beInterestedEntities={}
        self.interestedEvents={}
        if 0:self.space=None  #type:Space

    #注册事件,当同房间的其他类发射事件时触发方法,可以多次调用只有一次效果
    def onSpace(self,messageName,func):
        self.space.registerMessage(messageName,self,func)

    def offSpace(self,messageName):
        self.space.deregisterMessage(self,messageName)

    def offSpaceAll(self):
        self.space.deregisterMessageClass(self)

    def fireSpace(self,msgName,*arg):
        self.space.fire(self,msgName,*arg)


    #注册事件,只有感兴趣的类发射的事件才触发方法
    def onInterest(self,msgName,func):
        if msgName not in self.interestedEvents:
            self.interestedEvents[msgName]=[]
        self.interestedEvents[msgName]=func.__name__

    def offInterest(self,msgName):
        del self.interestedEvents[msgName]

    def offAllInterestedEvents(self):
        self.interestedEvents={}


    #对某个类感兴趣
    def interest(self, en):
        # noinspection PyUnresolvedReferences
        en.beInterestedEntities[self.id]=self
        self.interestedEntities[en.id]=en


    def uninterest(self, en):
        if en.id in self.interestedEntities:
            del self.interestedEntities[en.id]
            # noinspection PyUnresolvedReferences
            del en.beInterestedEntities[self.id]

    def uninterestAll(self):
        for id,en in self.interestedEntities.items():
            # noinspection PyUnresolvedReferences
            del en.beInterestedEntities[self.id]
        self.interestedEntities.clear()


    def fire(self,msgName,*arg):
        if len(self.beInterestedEntities):
            for id,en in tuple(self.beInterestedEntities.items()):
                if 0:en=en #type:EventSystem
                if msgName in en.interestedEvents:
                    getattr(en, en.interestedEvents[msgName])(*arg)



    def offAllEvent(self):
        self.offSpaceAll()
        self.uninterestAll()
        self.offAllInterestedEvents()
