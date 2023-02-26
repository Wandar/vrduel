# -*- coding: utf-8 -*-
import collections

import os
import re

import sys

import json

userTypeFilePath = 'scripts/user_type/'
sys.path.append(userTypeFilePath)
import UserType
# noinspection PyUnresolvedReferences
import lib.xmltodictOrderd

SERVER_TYPE_TO_TSTYPE={
    "UINT8":"number",
    "INT8":"number",
    "INT16":"number",
    "UINT16":"number",
    "INT32":"number",
    "UINT32":"number",
    "INT64":"number",
    "UINT64":"number",
    "FLOAT":"number",
    "DOUBLE":"number",
    "STRING":"string",
    "UNICODE":"string",
    "VECTOR2":"cc.Vec2",
    "VECTOR3":"Vector3",
    "VECTOR4":"Vector4",
    "ENTITYCALL":None,
    "BOOL":'boolean',
    "U8SCALE":"number",
    "I8RAD":"number",

    "ID":"number",
}

#
# def xmltojson(xmlstr):
#     # parse是的xml解析器
#     #有bug,解析数组会出错
#     xmlparse = lib.xmltodictOrderd.parse(xmlstr)
#     # json库dumps()是将dict转化成json格式，loads()是将json转化成dict格式。
#     # dumps()方法的ident=1，格式化json
#     # jsonstr = json.dumps(xmlparse,indent=1)
#     return xmlparse

# import time
# f=open("d_item.fods",encoding="utf-8")
# xstr=f.read()
# f.close()
# # print(xstr)
# t1=time.time()
# j=xmltojson(xstr)
# t2=time.time()-t1
# print("use time ",t2)
# print(j)
# exit()
#使用时间80ms

def jsontoxml(j):
    # xmltodict库的unparse()json转xml
    xmlstr = lib.xmltodictOrderd.unparse(j, pretty=True)
    # xmlstr=xmltodict.unparse(j,pretty=True)
    return xmlstr

# 'DebugSpaceCE.py':truePath
allComs = {}


def genAllComs(path="."):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            genAllComs(item_path)
        elif os.path.isfile(item_path):
            if "pyc" not in item:
                allComs[item] = item_path


# allFileSigns={}
# def getAllFileSign():

def ERROR_MSG(*args):
    print(*args)
    exit()

def _getStrFirstLetter(s):
    for i in s:
        if i!=' ':
            return i

def _isLineCommented(s):
    if _getStrFirstLetter(s)=='#':
        return True
    return False


# def testFunc得到名字 没有名字返回False 被注释返回True
def _defFuncGetName(s):
    defNum = s.find('def ')
    if defNum:
        pre = defNum + 4
        s = s[pre:]
        end = s.find('(')
        s = s[:end]
        return s
    else:
        return None


# c_testArg=0
def _argGetNameAndVal(s):
    commentpos=s.find("#")
    if commentpos!=-1:
        s=s[:commentpos]
    s = s.replace(" ", "")
    l = s.split('=')
    if len(l[0]) > 0:
        return l
    else:
        return None


def _removeArrSpace(arr):
    for i in range(len(arr) - 1, -1, -1):
        if arr[i] == '':
            del arr[i]


# input #p UINT8
def _getTypes(s):
    arr = s.split(' ')
    _removeArrSpace(arr)
    return arr


def test():
    f = open('../scripts/cell/c/AvatarCE.py', encoding='utf-8')
    s = f.read()
    arr = s.split('\n')
    # print(arr)
    for i in range(len(arr)):
        s = arr[i]
        if s.find("#p") >= 0:
            # print(_defFuncGetName(arr[i+1]))
            print(_getTypes(s))
    f.close()


SHORT_TYPE_DICT = {
    'BASE': 'BASE',
    'BASEC':'BASE_AND_CLIENT',
    "CELL": "CELL_PRIVATE",
    "ALL": "ALL_CLIENTS",
    "OWN": "OWN_CLIENT",
    "OTHER": "OTHER_CLIENTS"
}


# 把#p #e的类型发送到d
# 返回添加到client的字符串

# {
#     "e_arg":''
#     "e_method":''
# }
def putFileToD(CEorBA, comName, d,clientStrs):
    fileName = comName + CEorBA + ".py"
    if fileName not in allComs:
        return
    filePath = allComs[fileName]
    if not os.path.exists(filePath):
        return
    f = open(filePath, encoding='utf-8')
    s = f.read()
    f.close()
    arr = s.split('\n')
    clientAddStr = ''

    for i in range(len(arr)):
        s = arr[i]
        if s.find("#p") >= 0:
            coms = s.split(' ')
            _removeArrSpace(coms)  # #p,UINT8,
            if coms[0] != '#p':  # 可能是#per这样的注释
                continue
            coms = coms[1:]
            if _isLineCommented(arr[i+1]):
                continue
            funName = _defFuncGetName(arr[i + 1])
            if not funName:
                ERROR_MSG("error empty line below ", s)
            if len(coms):
                funcDic = collections.OrderedDict()
                funcDic["Arg"]=coms
            else:
                funcDic = None
            if CEorBA == 'CE':
                d["root"]["CellMethods"][funName] = funcDic
            elif CEorBA == 'BA':
                d["root"]["BaseMethods"][funName] = funcDic
        elif s.find("#e") >= 0:
            coms = s.split(' ')
            _removeArrSpace(coms)  # #p,UINT8,
            if coms[0] != '#e':  # 可能是#per这样的注释
                continue
            coms = coms[1:]
            if _isLineCommented(arr[i+1]):
                continue
            funName = _defFuncGetName(arr[i + 1])
            if not funName:
                ERROR_MSG("error empty line below ", s)
            if len(coms):
                funcDic =collections.OrderedDict()
                funcDic["Exposed"]= None
                funcDic["Arg"]= coms

            else:
                funcDic =collections.OrderedDict()
                funcDic["Exposed"]= None
            if CEorBA == 'CE':
                d["root"]["CellMethods"][funName] = funcDic
            elif CEorBA == 'BA':
                d["root"]["BaseMethods"][funName] = funcDic
            clientAddStr += _genClient_e_func(funName, CEorBA, coms)

        elif s.find("#c") >= 0:
            coms = s.split(' ')
            _removeArrSpace(coms)  # #p,UINT8,
            if coms[0] != '#c':  # 可能是#per这样的注释
                continue
            coms = coms[1:]
            if len(coms) and coms[0] in ('BASE','BASEC', 'CELL', 'ALL', 'OWN', 'OTHER'):  # 是成员不是函数
                if _isLineCommented(arr[i+1]):
                    continue
                argName,val = _argGetNameAndVal(arr[i + 1])
                if not argName:
                    ERROR_MSG("arg name not found", s)
                temp = collections.OrderedDict()
                temp["Type"]= coms[1]
                temp["Flags"]= SHORT_TYPE_DICT[coms[0]]
                d["root"]["Properties"][argName]=temp
                valDe=None
                for m in range(len(coms)):
                    if coms[m]=="DBLEN":
                        temp["DatabaseLength"]=coms[m+1]
                    elif coms[m]=="STORED":
                        temp['Persistent']='true'
                    elif coms[m]=='INDEX':
                        temp['Index']=coms[m+1]
                    elif coms[m]=="DE":
                        valDe=coms[m+1]

                if valDe!=None:
                    temp['Default']=valDe
                elif val=='""':
                    pass
                elif val!="None":
                    if temp["Type"]=="BOOL":
                        if val=="True":
                            val='1'
                        elif val=="False":
                            val='0'
                    val=val.replace('"','')
                    # if bool(re.search('[a-zA-Z]', val)):#是字符串
                    #     print("error val = ",argName,val)
                    temp['Default']=val
                if coms[0]=='ALL' or coms[0]=='OWN' or coms[0]=='OTHER' or coms[0]=='BASEC':
                    typeStr=_typeStrToClientType(coms[1])
                    if typeStr:
                        clientStrs['e_arg']+='\n    %s:%s'%(argName,typeStr)
                    else:
                        clientStrs['e_arg']+='\n    %s'%argName

            else:  # 是函数
                if _isLineCommented(arr[i+1]):
                    continue
                funName = _defFuncGetName(arr[i + 1])
                if not funName:
                    ERROR_MSG("error empty line below ", s)
                if len(coms):
                    funcDic = collections.OrderedDict()
                    funcDic["Arg"]= coms
                else:
                    funcDic = None
                d["root"]["ClientMethods"][funName] = funcDic

    clientStrs['e_method']+=clientAddStr

    # elif s.find("#e ")>=0:


def _createDefaultDef():
    d = collections.OrderedDict()
    d["root"] = collections.OrderedDict()
    root = d["root"]
    root["Properties"] = collections.OrderedDict()
    root["BaseMethods"] = collections.OrderedDict()
    root["CellMethods"] = collections.OrderedDict()
    root["ClientMethods"] = collections.OrderedDict()
    return d


#         e_switchGun(num){
#             this.cellCall("e_switchGun",num)
#         }
def _genClient_e_func(funcName, CEorBA, argList):
    argStr = ''
    for i in range(len(argList)):
        arg = argList[i]
        argStr += arg+'_'+str(i)
        if len(argList) - 1 != i:
            argStr += ','
    callStr=""
    if CEorBA == "CE":
        callStr = 'cellCall'
    elif CEorBA == "BA":
        callStr = 'baseCall'
    else:
        assert "not CE BA %s"%CEorBA
    return '\n    ' + funcName + '(' + argStr + '){\n' + '        this.' + callStr + '("' + funcName + '",' + argStr + ')\n    }'

def getClientPath():
    f=open('clientPath.txt','r',encoding="utf-8")
    j=f.read()
    f.close()
    return j
clientPath=getClientPath()

def addClientStr(trueComName, str_e_method, str_c_arg):
    clientComPath = clientPath + 'assets/scripts/client/c/' + trueComName + 'CL.ts'
    if not os.path.exists(clientComPath):
        # ERROR_MSG("not found client ", trueComName,str_e_method, str_c_arg)
        return

    with open(clientComPath, 'r', encoding='utf-8') as f:
        s=''
        if str_e_method:
            s = f.read()
            a = s.find("//e_methods")
            if a < 0:
                ERROR_MSG("client not has //e_methods ", trueComName)
            before = s[:a + 11]
            after = s[a + 11:]
            end = after.find('//end_e_methods')
            after = after[end:]
            s = before + str_e_method + '\n    ' + after

        if str_c_arg:
            if not s:
                s=f.read()
            a = s.find("//c_arg")
            if a < 0:
                ERROR_MSG("client not has //c_arg ", trueComName)
            before = s[:a + 7]
            after = s[a + 7:]
            end = after.find('//end_c_arg')
            after = after[end:]
            s = before + str_c_arg + '\n    ' + after
    with open(clientComPath, 'w', encoding='utf-8') as f:
        f.write(s)





def genXML():
    genAllComs(r"./scripts/cell/c")
    genAllComs(r"./scripts/base/c")
    interfacePath = "./scripts/entity_defs/interfaces/"
    for comName in os.listdir(interfacePath):
        if "Com.def" in comName:
            d = _createDefaultDef()
            trueName = comName.replace("Com.def", "")
            clientStrs={
                "e_method":'',
                'e_arg':''
            }
            putFileToD("CE", trueName, d,clientStrs)
            putFileToD("BA", trueName, d,clientStrs)
            s = jsontoxml(d)
            with open(interfacePath + comName, 'w') as f:
                f.write(s)
            #下面的注释掉了如果没有clientStr的话会消掉文件内容,原因不明
            # if clientStrs["e_method"] or clientStrs["e_arg"]:
            #     addClientStr(trueName, clientStrs["e_method"],clientStrs["e_arg"])
    print("genXML success")


# <ItemData>FIXED_DICT
# <implementedBy>UserType.ItemData</implementedBy>
# <Properties>
# <itemID>
# <Type>UINT16</Type>
# </itemID>
# <itemUUID>
# <Type>UINT32</Type>
# </itemUUID>
# <num>
# <Type>UINT16</Type>
# </num>
# </Properties>
# </ItemData>

def syncUserTypeAlias():
    sserver = ''#到alias.xml
    sclient=''#到UserType.ts
    for name in dir(UserType):
        if name[:2] == '__':
            continue
        Type = getattr(UserType, name)
        if name != 'UserType' and getattr(Type, 'ATTR',None):
            sserver+='\n    <{0}>FIXED_DICT\n' \
                     '        <implementedBy>UserType.{0}</implementedBy>\n' \
                     '        <Properties>\n' .format(name)
            sserver_end='        </Properties>\n' \
                 '    </{0}>'.format(name)

            for attrname,typeStr in Type.ATTR.items():
                if typeStr[:5]!='LIST_':
                    sserver+='            <{0}>\n' \
                             '                <Type>{1}</Type>\n' \
                             '            </{0}>\n'.format(attrname,typeStr)
                else:#是数组
                    typeStr=typeStr[5:]
                #     <Type>ARRAY
                #     <of>AccountData</of>
                # </Type>
                    sserver+='            <{0}>\n' \
                             '                <Type>ARRAY\n' \
                             '                    <of>{1}</of>\n' \
                             '                </Type>\n' \
                             '            </{0}>\n'.format(attrname,typeStr)
            sserver+=sserver_end

    with open('./scripts/entity_defs/types.xml', 'r', encoding='utf-8') as f:
        s = f.read()
        a = s.find("##generate-->")
        if a < 0:
            ERROR_MSG("alias not has")
        before = s[:a + 13]
        after = s[a + 13:]
        end = after.find('<!--end_generate##')
        after = after[end:]
        newStr = before + sserver + '\n    ' + after
    with open('./scripts/entity_defs/types.xml', 'w', encoding='utf-8') as f:
        f.write(newStr)




def _typeStrToClientType(typeStr):
    if typeStr in SERVER_TYPE_TO_TSTYPE:
        typeStr=SERVER_TYPE_TO_TSTYPE[typeStr]
    elif typeStr[:5]=='LIST_':
        t=typeStr[5:]
        if t in SERVER_TYPE_TO_TSTYPE:
            t=SERVER_TYPE_TO_TSTYPE[t]
        typeStr=t+'[]'
    elif typeStr[-5:]=='_LIST':
        t=typeStr[:-5]
        if t in SERVER_TYPE_TO_TSTYPE:
            t=SERVER_TYPE_TO_TSTYPE[t]
        typeStr=t+'[]'
    return typeStr

# export interface ItemData{
#     itemID:number,
#     num:number,
#     itemUUID:number
#     engineID:number,
# }
def syncUserTypeClient():
    sclient = ''
    for name in dir(UserType):
        if name[:2] == '__':
            continue
        Type = getattr(UserType, name)
        if name != 'UserType' and getattr(Type, 'ATTR',None) and getattr(Type,"__genClient__",True):
            sclient+='\nexport interface %s{\n'%name
            sserver_end='}\n'

            for attrname,typeStr in Type.ATTR.items():
                typeStr=_typeStrToClientType(typeStr)
                if typeStr:
                    sclient+='    {0}:{1},\n'.format(attrname,typeStr)
                else:
                    sclient+='    {0},\n'.format(attrname)

            sclient+=sserver_end

    cPath=clientPath + 'assets/scripts/client/user_type/UserType.ts'
    with open(cPath, 'r', encoding='utf-8') as f:
        s = f.read()
        a = s.find("///generate")
        if a < 0:
            ERROR_MSG("alias not has")
        before = s[:a + 11]
        after = s[a + 11:]
        end = after.find('//end_generate')
        after = after[end:]
        newStr = before + sclient + '\n' + after
    with open(cPath, 'w', encoding='utf-8') as f:
        f.write(newStr)


if __name__ == '__main__':
    """
    遍历所有c内的组件,然后找出Cell和Base,根据CE和BA的描述符重新生成Com还有Client
    同步UserType.py到types.xml
    """
    genXML()
    syncUserTypeAlias()
    # syncUserTypeClient()
