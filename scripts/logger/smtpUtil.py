#! /usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import platform
import sys

import KBEngine
import smtplib
from email.mime.text import MIMEText
import time


m163USER=""
m163PASS=""
try:
    sys.path.append(os.getenv("curpath")+"/sec")
    import secfile
    m163USER=secfile.MAILLOGGER163USER
    m163PASS=secfile.MAILLOGGER163PASS
except:
    pass

#25端口被封
# def sendMailSmtp(sub, content):
#     to_list=mailto_list
#     me="hello"+"<"+mail_user+"@"+mail_postfix+">"
#     msg = MIMEText(content,_subtype='plain')
#     msg['Subject'] = sub
#     msg['From'] = me
#     msg['To'] = ";".join(to_list)                #将收件人列表以‘；’分隔
#     try:
#         server = smtplib.SMTP()
#         server.connect(mail_host)                            #连接服务器
#         server.login(mail_user,mail_pass)               #登录操作
#         server.sendmail(me, to_list, msg.as_string())
#         server.close()
#         return True
#     except Exception as e:
#         KBEDebug.ERROR_MSG("send error",e)
#         return False


def sendMailSSL(sub,content):
    if "Windows" in platform.platform():
        return True

    if m163USER=="" or m163PASS=="":
        return True

    KBEngine.scriptLogType(KBEngine.LOG_TYPE_INFO)

    mailto_list=[m163USER]           #收件人(列表)
    mail_host="smtp.163.com"            #使用的邮箱的smtp服务器地址，这里是163的smtp地址
    mail_pass=m163PASS

    t1=time.time()
    msg = MIMEText(content,_subtype='plain')
    from_addr=mailto_list[0]
    to_addr=mailto_list[0]
    msg['From'] = u'<%s>' % from_addr
    msg['To'] = u'<%s>' % to_addr
    msg['Subject'] = sub

    try:
        smtp = smtplib.SMTP_SSL(mail_host, 465,timeout=10)
        smtp.set_debuglevel(0)
        smtp.ehlo(mail_host)
        smtp.login(from_addr, mail_pass)
        smtp.sendmail(from_addr, [to_addr], msg.as_string())
        result=True
    except Exception as e:
        print("mailsend error",e)
        result=False

    print("mailsend time=",time.time()-t1)
    return result