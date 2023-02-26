# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as ET

import json


def getClientPath():
    f=open('../clientPath.txt','r',encoding="utf-8")
    j=f.read()
    f.close()
    return j
def createEntity():
    className = input("Enter your Class: ")
    if not className:
        exit()
    hasBase=input('has Base? y/n(y):')

    if not hasBase:
        hasBase='y'
    if hasBase=='y':
        with open('./createEntityTemplate/base.py', 'r') as f:
            txt=f.read()
        a=txt.replace("XXXX",className)
        with open("../scripts/base/%s.py"%className,'w') as f:
            f.write(a)

    hasCell =input('has cell? y/n(y):')
    if not hasCell:
        hasCell='y'
    if hasCell=='y':
        with open('./createEntityTemplate/cell.py', 'r') as f:
            txt=f.read()
        a=txt.replace("XXXX",className)
        with open("../scripts/cell/%s.py"%className,'w') as f:
            f.write(a)


    with open('./createEntityTemplate/def.def', 'r') as f:
        txt=f.read()
    a=txt.replace("XXXX",className)
    with open("../scripts/entity_defs/%s.def"%className,'w') as f:
        f.write(a)

    entityXml=ET.parse("../scripts/entities.xml")
    root = entityXml.getroot()
    a=ET.Element(className)
    hasClient=input("hasClient? y/n(y):")
    if not hasClient:
        hasClient='y'
    if hasClient=='y':
        a.set("hasClient","true")
    root.append(a)
    entityXml.write("../scripts/entities.xml")
    if hasClient=='y':
    #     clientPath = getClientPath()+'assets/scripts/client/'
    #     #client
    #     with open('./createEntityTemplate/client.ts', 'r') as f:
    #         txt=f.read()
    #     a=txt.replace("XXXX",className)
    #     with open(clientPath+"%s.ts"%className,'w') as f:
    #         f.write(a)
        #bot
        with open('./createEntityTemplate/bot.py', 'r') as f:
            txt=f.read()
        a=txt.replace("XXXX",className)
        with open("../scripts/bots/%s.py"%className,'w') as f:
            f.write(a)



    print("create %s ok"%className)



createEntity()