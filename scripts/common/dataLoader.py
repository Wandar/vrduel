# -*- coding: utf-8 -*-
import json
import xml.dom.minidom
from xml.dom.minidom import parse

try:
    import KBEngine
    import reloadSystem
    from KBEDebug import *
    import util
except ImportError:
    def INFO_MSG(*args):
        print(*args)


    def ERROR_MSG(*args):
        print(*args)

if 0: from cellapp import KBEngine

_switchs = {
    "NONE": 0,
    "WHITE": 1,
    "BLACK": 2,
    "RED": 3,
    "GREEN": 4,

    "MONSTER": 1,

}

D_CARD = {}


def cardDataFilterFunc(l):
#     for item in l:
#         if not item["package"] and not item["prefab"]:
#             item["package"]=item["prefab"]=item["key"]
#         elif not item["prefab"]:
#             item["prefab"]=item["key"]
#         elif not item["package"] and item["prefab"]:
#             ERROR_MSG("not has package but has prefab",item)
    for item in l:
        checkCardData(item)
    return l


allDataConfig = {
    "sec/data/data.fods": [
        {
            "name": "D_CARD",
            "serverpath": "scripts/server_common",
            "d": D_CARD,
            "porttype": "list",
            "id": "id",
            "uniquekeys":["id","key"],
            "sheet": ["page1","test"],
            "func": cardDataFilterFunc,
            "hasClient": True
        }
    ]
}



def reloadData():
    if KBEngine.isDebugVer():
        reloadDataDebug()
    else:
        reloadDataRelease()
    reloadSystem.reloadAllObjectsData()


def reloadDataDebug():
    for key, dataConfigList in allDataConfig.items():
        for dataConfig in dataConfigList:
            f = util.openRes(dataConfig["serverpath"] + "/" + dataConfig["name"] + ".json", 'r')

            if dataConfig["porttype"] == "list":
                l = None
                try:
                    l = json.loads(f.read())
                except:
                    ERROR_MSG(dataConfig["name"] + " parse error")

                if l:
                    checkDupli(l,dataConfig["uniquekeys"])
                    jTemp = {}
                    for item in l:
                        jTemp[item[dataConfig["id"]]] = item
                    dataConfig["d"].clear()
                    _copyJson(dataConfig["d"], jTemp)
            else:
                ERROR_MSG("iauvbcsuyavcuaycvauy")

            f.close()
            INFO_MSG("reload clientdata ok ", dataConfig["name"])

def reloadDataRelease():
    for key, dataConfigList in allDataConfig.items():
        allSheets = parse_fods(KBEngine.getResFullPath(key))
        for dataConfig in dataConfigList:
            if type(dataConfig["sheet"]) != list:
                sheet = getSheet(allSheets, dataConfig["sheet"])
                l = sheetToArray(dataConfig["name"], sheet, False)
            else:
                l = []
                for sheetName in dataConfig["sheet"]:
                    sheet = getSheet(allSheets, sheetName)
                    partJ = sheetToArray(dataConfig["name"], sheet, False)
                    l+=partJ

            if dataConfig["func"]:
                l = dataConfig["func"](l)

            checkDupli(l,dataConfig["uniquekeys"])
            jTemp=arrayToJson(l,dataConfig["id"])
            dataConfig["d"].clear()
            _copyJson(dataConfig["d"], jTemp)
            INFO_MSG("reload ok ", dataConfig["name"])



def arrayToJson(l,key):
    j={}
    for item in l:
        j[item[key]]=item
    return j

def checkDupli(l,keys):
    check={}
    if type(l)==list:
        for key in keys:
            for a in l:
                val=a[key]
                if val in check:
                    ERROR_MSG("!!!!!!!!!!!!!!!!!!!!!!!!!!duplicate val =",val)
                check[val]=True
    else:
        ERROR_MSG('not list')


def checkCardData(item):
    if item["id"]==0:
        if len(item["name_en"].split('.'))!=3:
            ERROR_MSG("version format error")
        return
    if not item["key"]:
        ERROR_MSG("not has key",item)
        return
    if not item["name_en"]:
        ERROR_MSG(item["key"]+" at least has an English name")
    if not item["category"]:
        ERROR_MSG("no category ",item)

#copy json to d
def _copyJson(d, json):
    for itemID, itemData in json.items():
        if itemID not in d:
            d[itemID] = {}
        for attrName in itemData:
            d[itemID][attrName] = json[itemID][attrName]



def _allToInt(arr):
    for i in range(len(arr)):
        arr[i] = int(arr[i])
    return arr


def _allToFloat(arr):
    for i in range(len(arr)):
        arr[i] = float(arr[i])
    return arr


def getFirstXmlNode(node, name):
    for a in node.getElementsByTagName(name):
        return a


#path带data/
def parse_fods(path):
    dom = xml.dom.minidom.parse(path)
    root = dom.documentElement
    spreadSheet = getFirstXmlNode(root, "office:spreadsheet")
    return spreadSheet


def getSheet(allSheet, sheetName):
    l = allSheet.getElementsByTagName("table:table")
    for sheet in l:
        name = sheet.getAttribute("table:name")
        if name == sheetName:
            return sheet.getElementsByTagName("table:table-row")
    ERROR_MSG("get Sheet not found")
    return None


def getLine(sheet, num):
    cellList = sheet[num].getElementsByTagName("table:table-cell")
    res = ()
    for cell in cellList:
        e = getFirstXmlNode(cell, "text:p")
        if e:
            txt = e.firstChild.nodeValue
        else:
            txt = ''
        repeatedNum = cell.getAttribute("table:number-columns-repeated")
        if repeatedNum:
            for i in range(int(repeatedNum)):
                res += (txt,)
        else:
            res += (txt,)
    return res


def sheetToArray(dataName, sheet, isClient=False):
    keys = getLine(sheet, 0)
    keyType = getLine(sheet, 1)
    toClient = getLine(sheet, 2)

    keyNum = len(keyType)

    mainKeyPos = []

    keys = list(keys)
    for i in range(len(keys)):
        k = keys[i]
        if '(key)' in k:
            k = k.replace('(key)', '')
            keys[i] = k
            mainKeyPos.append(i)
    if not len(mainKeyPos):
        mainKeyPos.append(0)

    l = []
    lineNum = len(sheet)
    for i in range(3, lineNum):
        dataarr = getLine(sheet, i)
        if len(dataarr) != keyNum:
            ERROR_MSG("len(dataarr)!=keyNum")
            continue

        #要两个主键都有的才能加入
        isValid = True
        for pos in mainKeyPos:
            if not dataarr[pos]:
                isValid = False
        if not isValid:
            continue

        jsonTemp = {}
        for j in range(len(keyType)):
            if not keyType[j]:
                continue
            if j >= len(dataarr):
                ERROR_MSG("dataarr over", j, keyType[j], dataName, len(dataarr), dataarr)
                continue
            datapre = dataarr[j]
            t = keyType[j]
            result = ""
            if t == 'NONE':
                pass
            elif t == 'BOOL':
                if datapre == "":
                    result = False
                elif datapre == "0":
                    result = False
                else:
                    result = True
            elif t == 'STR':
                result = datapre
            elif t == 'INT':
                if datapre == "":
                    datapre = 0
                result = int(datapre)
            elif t == 'FLOAT':
                if datapre == "":
                    datapre = 0
                result = float(datapre)
            # elif t == 'FRAME':
            #     if datapre == "":
            #         datapre = 0
            #     result = int(datapre) * TICK_TIME
            elif t == 'INT_ARRAY':
                if datapre == "":
                    result = []
                else:
                    datapre = datapre.replace('"', '')
                    temp = datapre.split(',')
                    result = _allToInt(temp)
            elif t == 'STR_ARRAY':
                if datapre == "":
                    result = []
                else:
                    datapre = datapre.replace('"', '')
                    result = datapre.split(',')
            elif t == 'FLOAT_ARRAY':
                if datapre == "":
                    result = []
                else:
                    datapre = datapre.replace('"', '')
                    temp = datapre.split(',')
                    result = _allToFloat(temp)
            elif t == 'VEC2':
                if datapre == "":
                    result = [0, 0]
                else:
                    datapre = datapre.replace('"', '')
                    temp = datapre.split(',')
                    if len(temp) != 2:
                        ERROR_MSG(id + 'pos!=2')
                    result = _allToFloat(temp)
            elif t == 'VEC2_ARRAY':
                if datapre == "":
                    result = []
                else:
                    datapre = datapre.replace('"', '')
                    temp = datapre.split('),(')
                    result = []
                    for mm in temp:
                        mm = mm.replace('(', '')
                        mm = mm.replace(')', '')
                        vec2 = mm.split(',')
                        if len(vec2) != 2:
                            ERROR_MSG(id + "vec2array error")
                        result.append(_allToFloat(vec2))
            elif t == 'VEC3_ARRAY':
                if datapre == "":
                    result = []
                else:
                    datapre = datapre.replace('"', '')
                    temp = datapre.split('),(')
                    result = []
                    for mm in temp:
                        mm = mm.replace('(', '')
                        mm = mm.replace(')', '')
                        vec2 = mm.split(',')
                        if len(vec2) != 3:
                            ERROR_MSG(id + "vec3array error")
                        result.append(_allToFloat(vec2))
            elif t == 'SWITCH':
                if datapre == "":
                    result = 0
                else:
                    if datapre not in _switchs:
                        ERROR_MSG("not reginoise switch " + datapre)
                    result = _switchs[datapre]
            elif t == "SWITCH_ARRAY":
                if datapre == "":
                    result = []
                else:
                    datapre = datapre.replace('"', '')
                    temp = datapre.split(',')
                    result = []
                    for s in temp:
                        if s not in _switchs:
                            ERROR_MSG("switch not found ", s)
                            return
                        result.append(_switchs[s])
            else:
                ERROR_MSG("unknow keyType" + keyType[j])
            if keyType[j] != 'NONE':
                if not isClient:
                    jsonTemp[keys[j]] = result
                elif isClient and toClient[j] == 'C':
                    jsonTemp[keys[j]] = result
        l.append(jsonTemp)

    return l