# -*- coding: utf-8 -*-
"""
Created on Sat Dec  8 19:08:20 2018

@author: Андрей
"""
import time
import json
from websocket import create_connection

ws = create_connection("ws://188.166.120.114:8020/ws/")
ws.send(json.dumps({"name":"andrei", "side":"ask", "price":19, "amount":10}))
result = ws.recv()
print("Received '%s'" % result)

ws.close()