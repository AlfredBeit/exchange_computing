# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 17:28:59 2018

@author: Андрей
"""
import datetime
"""
valid json:
    {"name":"anyname", "side":"ask" or "bid", "price":integer, "amount":integer}
"""

class LimitOrderBook:
    
    __slots__ = ['con', 'maxp', 'valid_keys', 'valid_names']
    
    def __init__(self, con):
        self.con = con
        self.maxp = float('inf')
        self.valid_keys = set(['name', 'side', 'price', 'amount', 'ident'])
        self.valid_names = set(['oleg', 'alfred', 'andrei'])
        
    def validate_order(self, order):
        if len(set(order.keys()) - self.valid_keys) == 0 and order['name'] in self.valid_names:
            return True
        else:
            return False
        
    def handle_order(self, order):
        if order['side'] == 'ask':
           supply = self.con.zrevrangebyscore('bid', order['price'], 0, withscores=True)
           if len(supply) == 0:
               self.con.zadd('ask', {order['ident']: order['price']})
               return {'added': str(datetime.datetime.now())}
           else:
               trade = supply[-1]
               self.con.zrem('bid', trade[0])
               return {'ident' : trade[0].decode("utf-8"), 'price': str(trade[1])}
        elif order['side'] == 'bid':
            supply = self.con.zrevrangebyscore('ask', self.maxp, order['price'], withscores=True)
            if len(supply) == 0:
               self.con.zadd('bid', {order['ident']: order['price']})
               return {'added': str(datetime.datetime.now())}
            else:
               trade = supply[0]
               self.con.zrem('ask', trade[0])
               return {'ident' : trade[0].decode("utf-8"), 'price': str(trade[1])}