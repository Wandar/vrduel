# -*- coding: utf-8 -*-
import os
import sys
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect

IP="localhost"
PORT=32564

order="reloadScript"


if len(sys.argv)>1:
    order=sys.argv[1]


class Client(object):
    def __init__(self, url):
        self.url = url
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.connect()
        self.ioloop.start()



    @gen.coroutine
    def connect(self):
        print("trying to connect")
        # noinspection PyBroadException
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception:
            print("connection error")
            os.system("pause")
        else:
            print("connected")
            self.run()

    @gen.coroutine
    def run(self):
        if order=="reloadScript":
            self.ws.write_message(order)
        elif order=="reloadData":
            self.ws.write_message(order)
        elif order=="resetServer":
            self.ws.write_message(order)
        else:
            print("no command"+str(order))
            os.system("pause")
        print("request %s"%order)
        while True:
            msg = yield self.ws.read_message()
            print("receivemsg ",msg)
            if msg[-2:]=='ok':
                self.ws.close()
                os.system("pause")

if __name__ == "__main__":
    print("order=%s address=%s:%d"%(order,IP,PORT))
    client = Client("ws://%s:%d"%(IP,PORT))
    os.system("pause")