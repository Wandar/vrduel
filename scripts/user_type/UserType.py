# -*- coding: utf-8 -*-
from __future__ import annotations
try:
    from dataLoader import D_CARD
    from KBEDebug import *
    from reloadSystem import Reload
    from UserTypeBase import UserType
    from Constants import *
    from allcards import allcardClass
except ImportError:
    D_ITEM = {0: 1}
    allcardClass={}
    class Reload:pass
    class UserType:pass


class MyType(UserType):
    cc = 0
    dd = 0
    ATTR = {
        "cc": "UINT8",
        "dd": "UINT8"
    }

    @staticmethod
    def createObjFromDict(jsonData):  #转为实际的类
        return MyType(jsonData.getDict())

    @staticmethod
    def getDictFromObj(obj):
        return obj.__dict__

    @staticmethod
    def isSameType(obj):
        #不要用isinstance,错误原因不明
        return obj.__class__.__name__ == "MyType"


#一张卡有:原本的id,饰品字符串
class CardData(UserType):
    __IS_CARD__=True
    id=0 #卡牌的id,最重要的部分
    ID=0 #卡牌是哪边的
    uniID=0 #卡牌的唯一id,在决斗中使用
    entityID=0 #实体id
    Class='' #no use 哪个职业的卡
    key=name = index = description = name_CN = ''
    category = race = school = Effects = '' #category是种类比如
    level=0
    mana = attack = defense= health = durability = armor = 0
    mana_0=attack_0=defense_0=health_0=0
    numTargets = 0
    cardID = 0 #no use不要使用
    aura = trigBoard = trigHand = trigDeck = deathrattle = trigEffect = None
    options, overload = (), 0
    info1 = info2 = None
    isFace=True #是否面朝上
    isVel=True #是否竖直
    color=0
    acce="" #accessory

    _NONE=None
    ATTR={
        "id":"INT32",
        "ID":"INT8",
        "uniID":"INT32",
        "entityID":"INT32",
        "mana":"INT8",
        "level":"UINT8",
        "attack":"INT16",
        "defense":"INT16",
        "health":"INT16",
        "isFace":"BOOL",
        "isVel":"BOOL",
        "color":"UINT8",
        "acce":"STRING"
    }

    @staticmethod
    def genDefaultAttr(cardID):
        d={
            "id":cardID,
            "ID":0,
            "uniID":0,
            "entityID":0,
            "mana":0,
            "level":0,
            "attack":0,
            "defense":0,
            "health":0,
            "isFace":0,
            "isVel":0,
            "color":0,
            "acce":""
        }
        return d

    @staticmethod
    def createCardClass(cardID,Game=None,ID=0):
        if cardID==0:
            return CardData.getNone()
        name = D_CARD[cardID]["key"]
        c=allcardClass[name](Game,ID)
        return c


    #此函数不应该被调用,客户端上传的只能是uniID,而不是CardData类
    #而下传到客户端的尽量是CardData的类,可以简化逻辑
    @staticmethod
    def createObjFromDict(jsonData):
        d=jsonData.getDict()
        if d["id"]==0:
            return CardData.getNone()

        #不应该创建
        ERROR_MSG("8yugaajhsbvcyujs")
        name=D_CARD[d["id"]]["key"]
        c=allcardClass[name](None,0)
        CardData.__init__(c,d)
        return c


    def __init__(self,dic=None):
        if dic:
            self.__dict__=dic


    def onReloadData(self):
        #被远程调用的重载策划数据指令
        pass

    def initData(self):
        if self.id==0:
            return
        j=D_CARD[self.id]
        self.name=j["name_en"]
        self.key=j["key"]
        self.attack_0=j["attack"]

    @staticmethod
    def getNone():
        if not CardData._NONE:
            CardData._NONE = CardData(CardData.genDefaultAttr(0))
        return CardData._NONE


    @staticmethod
    def isValid(cardData):
        if not cardData:
            return False
        if cardData.id!=0:
            return True
        return False


    @staticmethod
    def getDictFromObj(obj):
        return obj.__dict__

    @staticmethod
    def isSameType(obj):
        return getattr(obj, "__IS_CARD__", False)

#
# class StoreDeckData(UserType):
#     name=""
#     data=""
#
#
#     ATTR={
#         "name":"UNICODE",
#         "data":"STRING"
#     }
#     """
#         "a":[]
#         "b":[]
#         "c":[]
#     """
#     def __init__(self,dic=None):
#         if dic:
#             self.__dict__=dic
#
#     def getNone(self):
#         StoreDeckData
#
#     @staticmethod
#     def createObjFromDict(jsonData):
#         return StoreDeckData(jsonData.getDict())
#     @staticmethod
#     def getDictFromObj(obj):
#         return obj.__dict__
#     @staticmethod
#     def isSameType(obj):
#         return obj.__class__.__name__=="StoreDeckData"




class DuelPlace(UserType):
    placeID=0
    p1=None
    p2=None
    ATTR={
        "placeID":"UINT8",
        "p1":"VECTOR3",
        "p2":"VECTOR3",
    }
    def __init__(self,dic=None):
        if dic:
            self.__dict__=dic

    @staticmethod
    def createObjFromDict(jsonData):
        return DuelPlace(jsonData.getDict())
    @staticmethod
    def getDictFromObj(obj):
        return obj.__dict__
    @staticmethod
    def isSameType(obj):
        return obj.__class__.__name__=="DuelPlace"


class BannerData(UserType):
    title=""
    text=""
    options=[]
    cb=""
    ATTR={
        "title":"STRING",
        "text":"STRING",
        "options":"LIST_STRING",
        "cb":"STRING",
    }
    def __init__(self,dic=None):
        if dic:
            self.__dict__=dic

    @staticmethod
    def createObjFromDict(jsonData):
        return BannerData(jsonData.getDict())
    @staticmethod
    def getDictFromObj(obj):
        return obj.__dict__
    @staticmethod
    def isSameType(obj):
        return obj.__class__.__name__=="BannerData"

# class ItemData(Reload,UserType):
#     __isItemData__ = True
#     __genClient__ = False  #不生成客户端
#
#     itemID = 0
#     num = 0
#     itemUUID = 0
#     UINT8_0 = 0
#     UINT16_0 = 0
#
#     NONE = None
#
#     ATTR = {
#         "itemID": "UINT16",
#         "num": "UINT16",
#         "itemUUID": "ID",
#         "UINT8_0": "UINT8",
#         "UINT16_0": "UINT16"
#     }
#
#     @staticmethod
#     def getNone():
#         if not ItemData.NONE:
#             ItemData.NONE = ItemData({
#                 "itemID": 0,
#                 "num": 0,
#                 "itemUUID": 0,
#                 "UINT8_0": 0,
#                 "UINT16_0": 0
#             })
#             DEBUG_MSG("create ItemData None")
#         return ItemData.NONE
#
#     def __init__(self, dic=None):
#         Reload.__init__(self,True,True)
#         if dic:
#             self.__dict__=dic
#             self.ITEM_BASE = D_ITEM[self.itemID]
#
#
#     #init when gen item
#     def initItem(self):
#         pass
#
#     def onReloadData(self):
#         self.ITEM_BASE = D_ITEM[self.itemID]
#
#     def getAllWeight(self):
#         occu = self.ITEM_BASE["occu"]
#         return self.num * occu
#
#     def isValid(self):
#         return self.itemID != 0
#
#     def dispatchFunc(self, funcName, *args):
#         func = getattr(self, funcName, None)
#         if func:
#             return func(*args)
#         else:
#             return False
#
#     @staticmethod
#     def createObj(itemID=0, num=0, itemUUID=0, UINT8_0=0, UINT16_0=0):
#         jsonData = {
#             "itemID": itemID,
#             "num": num,
#             "itemUUID": itemUUID,
#             "UINT8_0": UINT8_0,
#             "UINT16_0": UINT16_0
#         }
#         name = D_ITEM[jsonData["itemID"]]["class"]
#         Class = getattr(ItemClasses, name)
#         return Class(jsonData)
#
#     @staticmethod
#     def getDictFromObj(obj):
#         return obj.__dict__
#
#     @staticmethod
#     def createObjFromDict(jsonData):
#         name = D_ITEM[jsonData["itemID"]]["class"]
#         Class = getattr(ItemClasses, name)
#         return Class(jsonData.getDict())
#
#     @staticmethod
#     def isSameType(obj):
#         return getattr(obj, "__isItemData__", False)



# try:
#     import ItemClasses
# except Exception:
#     pass
