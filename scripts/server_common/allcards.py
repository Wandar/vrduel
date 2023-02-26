# -*- coding: utf-8 -*-
from util import *
import inspect
import importlib


allcardClass={}

def mergeAllCards(isReload=False):
    global allcardClass
    #注意全局变量不能赋值
    allcardClass.clear()

    INFO_MSG("merge all cards")

    mo=importlib.import_module("cards.cardPack1")
    # from cards import cardPack1
    # if isReload:
    #     mo=importlib.reload(mo)
    for name,Cls in inspect.getmembers(mo):
        if getattr(Cls,'__IS_CARD__',False):
            if name[0:2]!="__":
                if name in allcardClass:
                    ERROR_MSG("cardpack already has class ",name)
                allcardClass[name]=Cls