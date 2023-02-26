# -*- coding: utf-8 -*-

import os

import json


def getClientPath():
    f=open('../clientPath.txt','r',encoding="utf-8")
    j=f.read()
    f.close()
    return j

def removeCom():
    className=input("enter remove componentName(without BA/CE)")
    if not className:
        exit()

    path="../scripts/base/c/%sBA.py"%className
    if os.path.exists(path):
        os.remove(path)
        print("remove%s"%path)

    path="../scripts/cell/c/%sCE.py"%className
    if os.path.exists(path):
        os.remove(path)
        print("remove%s"%path)

    clientPath = getClientPath()+'assets/scripts/client/c/'
    path=clientPath+"%sCL.ts"%className
    if os.path.exists(path):
        os.remove(path)
        print("remove%s"%path)

    path="../scripts/entity_defs/interfaces/%sCom.def"%className
    if os.path.exists(path):
        os.remove(path)
        print("remove%s"%path)

removeCom()
