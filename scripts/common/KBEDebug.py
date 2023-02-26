# -*- coding: utf-8 -*-
import platform
import KBEngine




def DEBUG_MSG(*args):
    if not KBEngine.publish():
        KBEngine.scriptLogType(KBEngine.LOG_TYPE_DBG)
        print(*args)

def TEMP_MSG(*args):
    if not KBEngine.publish():
        KBEngine.scriptLogType(KBEngine.LOG_TYPE_DBG)
        print(*args)

def TEMP_ERROR(*args):
    KBEngine.scriptLogType(KBEngine.LOG_TYPE_ERR)
    print(*args)

def INFO_MSG(*args):
    KBEngine.scriptLogType(KBEngine.LOG_TYPE_INFO)
    print(*args)


def WARNING_MSG(*args):
    KBEngine.scriptLogType(KBEngine.LOG_TYPE_WAR)
    print(*args)
    KBEngine.scriptLogType(KBEngine.LOG_TYPE_INFO)


def ERROR_MSG(*args):
    KBEngine.scriptLogType(KBEngine.LOG_TYPE_ERR)
    print(*args)
    KBEngine.scriptLogType(KBEngine.LOG_TYPE_INFO)


LOGGER_EMAIL = "This is should email="
EMAIL_TITLE_END = "#emailend#"
def MAIL_MSG(title,msg):
    if "Windows" not in platform.platform():
        KBEngine.scriptLogType(KBEngine.LOG_TYPE_ERR)
        print(LOGGER_EMAIL+title+EMAIL_TITLE_END+msg)
        KBEngine.scriptLogType(KBEngine.LOG_TYPE_INFO)

def ASSERT_MSG(cond,*args):
    if not cond:
        KBEngine.scriptLogType(KBEngine.LOG_TYPE_ERR)
        print(*args)
        KBEngine.scriptLogType(KBEngine.LOG_TYPE_INFO)
