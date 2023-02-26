# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET

import json


def getClientPath():
    f=open('../clientPath.txt','r',encoding="utf-8")
    j=f.read()
    f.close()
    return j
def removeEntity():
    className=input("remove Class Name:")
    path="../scripts/cell/%s.py"%className
    if os.path.exists(path):
        os.remove(path)
        print("remove%s"%path)
    path="../scripts/base/%s.py"%className
    if os.path.exists(path):
        os.remove(path)
        print("remove%s"%path)
    path="../scripts/entity_defs/%s.def"%className
    if os.path.exists(path):
        os.remove(path)
        print("remove%s"%path)
    path = getClientPath()+'assets/scripts/client/%s.ts'%className
    if os.path.exists(path):
        os.remove(path)
        print("remove%s"%path)
    path="../scripts/bots/%s.py"%className
    if os.path.exists(path):
        os.remove(path)
        print("remove%s"%path)

    entityXml=ET.parse("../scripts/entities.xml")
    root = entityXml.getroot()
    AA=root.find(className)
    root.remove(AA)
    entityXml.write("../scripts/entities.xml")
    print("remove ok")

removeEntity()