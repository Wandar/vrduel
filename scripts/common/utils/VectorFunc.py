# -*- coding: utf-8 -*-
import KBEngine
import math

import random
# noinspection PyUnresolvedReferences
from Math import *
from Constants import *
from KBEDebug import *

if 0:
    from KBEMath.Math import *


OUTER_POS=(-100000,-100000)

tempVector2=Vector2(0,0)

# tempVector2_1=Vector2(0,0)
# tempVector3=Vector3(0,0,0)
# tempVector3_1=Vector3(0,0,0)

# def releaseGlobalVectors():
#     global ZERO_VECTOR3
#     global OUTER_VECTOR
#
#     global tempVector2
#     global tempVector2_1
#     global tempVector3
#     global tempVector3_1
#
#     ZERO_VECTOR3=None
#     OUTER_VECTOR=None
#
#     tempVector2=None
#     tempVector2_1=None
#     tempVector3=None
#     tempVector3_1=None

def meterVec3ToPixelXY(v):
    return (v.x*TO_PIXEL,v.z*TO_PIXEL)

def pixelXYToMeterVec3(x,y):
    return Vector3(x*TO_METER,0,y*TO_METER)

def pixelV2ToMeterV3(pos):
    return (pos[0]*TO_METER,0,pos[1]*TO_METER)

def ccposToTuple(ccpos):
    return (ccpos["x"],ccpos["y"])


def pSetLength(p,l):
    p=pNormalise(p)
    return p[0]*l,p[1]*l

#朝一个方向走l的距离换成PDirLen
# def pMoveDis(p,rad,l):
#     return pAdd(p,pMult(radiansToVector2(rad),l))


#注意出界
def pRand(p,fuzzy):
    return p[0]+random.randint(-fuzzy,fuzzy),p[1]+random.randint(-fuzzy,fuzzy)

# def randPosInCircle(circlePos,r):
#     jiaodu=random.uniform(0,math.pi*2)
#     randr=random.uniform(0,r)
#     vec=Vector3()
#     radiansToVector3(jiaodu,vec)
#     vec*=randr
#     vec+=circlePos
#     return vec

"""
#vector func
"""

# def vec3ToStr(vec):
#     return str(vec.x)+','+str(vec.y)+','+str(vec.z)

def pInRect(pos,xmin,xmax,ymin,ymax):
    return xmin<=pos[0]<=xmax and ymin<=pos[1]<=ymax

def vec2ToStr(vec):
    return str(vec.x)+','+str(vec.y)

def radiansToVector2(rad): # type: (float) -> tuple
    return math.sin(rad),math.cos(rad)

def vec2ToRadians(vec2): # type: (Vector2) -> float
    return math.atan2(vec2.x, vec2.y)


# def radiansToVector3(rad, gvec):
#     gvec.set(math.sin(rad), 0, math.cos(rad))
#     return gvec
# def vec3ToRadians(vec3):
#     return math.atan2(vec3.x, vec3.z)


def vector2to3(vector2, gvec3):
    gvec3.set(vector2.x, 0, vector2.y)
    return gvec3


def vector3to2(vector3):
    return Vector2(vector3.x, vector3.z)


def vec3EqualToVec3(vec3, vec3_2):
    if vec3.x == vec3_2.x and vec3.y == vec3_2.y and vec3.z == vec3_2.z:
        return True
    else:
        return False


def vec3IsZero(vec3):
    if vec3.x or vec3.z or vec3.y:
        return False
    else:
        return True


def vec3ToStr(vec3):
    return vec3.x+","+vec3.y+","+vec3.z

# def setNo0Dir(vmaster, x, z, length):
#     if x == 0 and z == 0:
#         radiansToVector3(random.uniform(-math.pi, math.pi), vmaster)
#     else:
#         vmaster.set(x, 0, z)
#     vmaster.normalise()
#     vmaster *= length

def randDirVec(): # type: () -> tuple
    return radiansToVector2(random.uniform(-math.pi, math.pi))


def vec3SubVec3(v1, v2, gvresult):
    gvresult.x = v1.x - v2.x
    gvresult.z = v1.z - v2.z


def vec3AddVec3(v1, v2, gvresult):
    gvresult.x = v1.x + v2.x
    gvresult.z = v1.z + v2.z


#带有g的参数是改变坐标,带有n的参数是受到引用
def vec3AddScaledVec3(gvmaster, v2, scaleNum):
    gvmaster.x += v2.x * scaleNum
    gvmaster.z += v2.z * scaleNum


def vec3SubVec3Norm(v1, v2):
    a = Vector3(v1)
    a -= v2
    a.normalise()
    return a


#vec31绕vec32瞬时针转X度
def vecRotateByVec(vec31, vec32, radians, vecResult):
    x = vec31.x
    y = vec31.z
    rx0 = vec32.x
    ry0 = vec32.z
    #瞬时针旋转
    x0 = (x - rx0) * math.cos(radians) + (y - ry0) * math.sin(radians) + rx0
    y0 = -(x - rx0) * math.sin(radians) + (y - ry0) * math.cos(radians) + ry0
    vecResult.set(x0, 0, y0)

# def pRotate(vec,rad):#顺时针转rad度
#     cos=math.cos(rad)
#     sin=math.sin(rad)
#     return vec[0]*cos+vec[1]*sin,-vec[0]*sin+vec[1]*cos


def pIsZero(p):
    if p[0]==0 and p[1]==0:
        return True
    return False

def pAdd(p1:tuple,p2:tuple):
    return p1[0]+p2[0],p1[1]+p2[1]

def pSub(p1,p2):
    return p1[0]-p2[0],p1[1]-p2[1]

#从p1到p2的方向
def pDirRad(p1,p2):
    return pToRadians(pSub(p2,p1))


def pMult(p1,num):
    return p1[0]*num,p1[1]*num

def pNeg(p):
    return -p[0],-p[1]


def xyVecToTuple(xyvec):
    return xyvec["x"],xyvec["y"]

def pToRadians(p):
    return math.atan2(p[0], p[1])

def pDot(p1,p2):
    return p1[0]*p2[0]+p1[1]*p2[1]

def pEqual(v1,v2):
    if v1[0]==v2[0] and v1[1]==v2[1]:
        return True
    return False

def pFuzzyEqual(v1,v2,fuzzy=0.1):
    if abs(v1[0]-v2[0])<fuzzy and abs(v1[1]-v2[1])<fuzzy:
        return True
    return False

def pReflect(pIn,pNormal):
    #入射向量和法线,入射向量可以不为normalise
    if pIsZero(pNormal):
        ERROR_MSG("pReflect normal =0,0")
        return 0,0
    pNormal=pNormalise(pNormal)
    return pSub(pIn,pMult(pNormal,2*pDot(pIn,pNormal)))

#一个坐标往另一个坐标移动distance,如果超过了,那就到vEnd上
def pMoveToP(v,vEnd,distance):
    d=pDistance(v,vEnd)
    if d<distance:
        return vEnd
    vSub=pSub(vEnd,v)
    vSub=pSetLength(vSub,distance)
    return pAdd(v,vSub)

#一个坐标往rad移动distance
def pMoveByRad(v,rad,distance):
    pV=pMult(radiansToVector2(rad),distance)
    return pAdd(pV,v)

def pIsAline(p1,p2,p3):
    v1=pSub(p1,p2)
    v2=pSub(p2,p3)
    if pDot(v1,v2)>0:
        return True
    else:
        return False


#v1 faceTo v2,return radians
def vec3FaceTo(v1,v2):
    return pToRadians((v1.x-v2.x,v1.z-v2.z))