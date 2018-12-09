# -*- coding: utf-8 -*-

import json
import redis
import tornado.ioloop
import tornado.web
import tornado.websocket

from tornado.options import define, options, parse_command_line

define("port", default=8888, type=int)
valid_names = set(['oleg', 'alfred', 'andrei'])

"""
valid json:
    {"name":"anyname", "side":"ask" or "bid", "price":integer, "amount":integer}
"""
con = redis.Redis('localhost', port=6379)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        print("New connection")
        self.write_message("Welcome!")

    def on_message(self, message):
        order = json.loads(message)
        if 'name' in order and order['name'] in valid_names:
            if order['side'] == 'ask':
               supply = con.zrevrangebyscore('bid', order['price'],0, withscores=True)
               if len(supply) == 0:
                   con.zadd('ask', {order['name']:order['price']})
                   self.write_message('your order has been added to the limit book')
               else:
                   trade = supply[-1]
                   con.zrem('bid', trade[0])
                   self.write_message('you bought from: ' + str(trade[0]) + ' price:' + str(trade[1]))
            elif order['side'] == 'bid':
                supply = con.zrevrangebyscore('ask', 99999,order['price'], withscores=True)
                if len(supply) == 0:
                   con.zadd('bid', {order['name']:order['price']})
                   self.write_message('your order has been added to the limit book')
                else:
                   trade = supply[0]
                   con.zrem('ask', trade[0])
                   self.write_message('you bought from: ' + str(trade[0]) + ' price:' + str(trade[1]))

    def on_close(self):
        print("Connection closed")

    def check_origin(self, origin):
        return True


app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/ws/', WebSocketHandler),
])


if __name__ == '__main__':
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()