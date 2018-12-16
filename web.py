# -*- coding: utf-8 -*-

import json
import redis
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define, options, parse_command_line
from LimitOrderBook import LimitOrderBook as lob

define("port", default=8888, type=int)

"""


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        print("New connection")
        self.write_message("Welcome!")

    def on_message(self, message):
        con = lob(self.application.con)
        order = json.loads(message)
        if con.validate_order(order):
            self.application.clientPool[order['ident']] = self
            trade = con.handle_order(order)  
            if 'added' in trade:
                self.write_message(json.dumps(trade))
            else:
                try:
                    value = self.application.clientPool[trade['ident']]
                    print(self.application.clientPool)
                    trade_msg = {'ident': order['ident'], 'price': trade['price']}
                    value.ws_connection.write_message(json.dumps(trade_msg))
                    self.write_message(json.dumps(trade))
                    repeat = False
                except KeyError:
                    self.write_message('failed')
    def on_close(self):
        for key in self.application.clientPool.keys():
            if self.application.clientPool[key] == self:
                self.application.clientPool[key] = None

    def check_origin(self, origin):
        return True

class Application(tornado.web.Application):
    def __init__(self):
        self.clientPool = {}
        self.con = redis.Redis('localhost', port=6379)
        handlers = (
                (r'/', IndexHandler),
                (r'/ws/', WebSocketHandler)
        )
        
        tornado.web.Application.__init__(self, handlers)

app = Application()

if __name__ == '__main__':
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()