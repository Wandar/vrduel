# -*- coding: utf-8 -*-
import json


def getClientPath():
    f=open('../clientPath.txt','r',encoding="utf-8")
    j=f.read()
    f.close()
    return j


def createCom():
    className=input("enter componentName(without BA/CE)")
    if not className:
        exit()
    hasBase=input('has Base? y/n(y):')

    if not hasBase:
        hasBase='y'
    if hasBase=='y':
        with open('./createEntityTemplate/baseComponent.py', 'r') as f:
            txt=f.read()
        a=txt.replace("XXXX",className)
        with open("../scripts/base/c/%sBA.py"%className,'w') as f:
            f.write(a)

    hasCell =input('has cell? y/n(y):')
    if not hasCell:
        hasCell='y'
    if hasCell=='y':
        with open('./createEntityTemplate/cellComponent.py', 'r') as f:
            txt=f.read()
        a=txt.replace("XXXX",className)
        with open("../scripts/cell/c/%sCE.py"%className,'w') as f:
            f.write(a)

    # hasClient =input('has client? y/n(y):')
    # if not hasClient:
    #     hasClient='y'
    # if hasClient=='y':
    #     clientPath = getClientPath()+'assets/scripts/client/c/'
    #     with open('./createEntityTemplate/clientCom.ts', 'r') as f:
    #         txt=f.read()
    #     a=txt.replace("XXXX",className)
    #     with open(clientPath+"%sCL.ts"%className,'w') as f:
    #         f.write(a)

    with open('./createEntityTemplate/component.def', 'r') as f:
        txt=f.read()
    a=txt.replace("XXXX",className)
    with open("../scripts/entity_defs/interfaces/%sCom.def"%className,'w') as f:
        f.write(a)

createCom()
