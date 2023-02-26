# -*- coding: utf-8 -*-
import reloadSystem
import KBEDebug

"""
注意,此类继承的类不能添加任何方法,此类只是为了dict的代码提示而存在
如果需要大规模
"""
FLOAT_TUPLE=("FLOAT","DOUBLE")


class UserType:
    _NONE=None
    ATTR={
    }
    def __init__(self,dic=None):
        if dic:
            self.__dict__=dic

    @staticmethod
    def getNone():
        pass

    def isNone(self):
        pass

    @staticmethod
    def createObjFromDict(jsonData):  #转为实际的类
        pass

    @staticmethod
    def getDictFromObj(obj):
        return obj.__dict__
    @staticmethod
    def isSameType(obj):
        return False

    def __eq__(self, other):
        KBEDebug.ERROR_MSG("dont eq ",self.__class__.__name__)
        return False

#所存的单位必须要有keyName的属性,以keyName来作为dict的键,里面的list直接就是KBEngine传输的list
class ListDict(dict):
    keyName="id"
    list=None
    def __init__(self, keyName="id", lforInit=None):
        dict.__init__(self)
        self.keyName=keyName
        if not lforInit:
            self.list=[]
        else:
            self.list=lforInit
            for en in lforInit:
                key=getattr(en,keyName)
                dict.__setitem__(self,key,en)

    def __setitem__(self, key, value):
        if key in self:
            i=self._isKeyInList(key)
            del self.list[i]
        self.list.append(value)
        dict.__setitem__(self,key,value)

    #返回序号,不存在返回None
    def _isKeyInList(self,key):
        for i in range(len(self.list)):
            if getattr(self.list[i],self.keyName)==key:
                return i
        return None

    def __delitem__(self, key):
        dict.__delitem__(self,key)
        i=self._isKeyInList(key)
        del self.list[i]

    def clear(self):
        dict.clear(self)
        self.list.clear()

#无统一keyName的版本,现在用不着
# class ListDict2(dict):
#     list=None
#     listOfKey=None
#     def __init__(self):
#         dict.__init__(self)
#         self.list=[]
#         self.listOfKey=[]
#
#     def __setitem__(self, key, value):
#         if key in self:
#             i=self._isKeyInList(key)
#             del self.list[i]
#             del self.listOfKey[i]
#         self.list.append(value)
#         self.listOfKey.append(key)
#         dict.__setitem__(self,key,value)
#
#     #返回序号,不存在返回None
#     def _isKeyInList(self,key):
#         for i in range(len(self.listOfKey)):
#             if self.listOfKey[i]==key:
#                 return i
#         return None
#
#     def __delitem__(self, key):
#         dict.__delitem__(self,key)
#         i=self._isKeyInList(key)
#         del self.list[i]
#         del self.listOfKey[i]
#
#     def clear(self):
#         dict.clear(self)
#         self.list.clear()