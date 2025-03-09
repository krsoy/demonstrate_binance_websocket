import requests
import urllib
import threading
import time
from functools import wraps
from Exchanges.framework.price_precision import *
# 有的币种价格精度并不是0.1起步，需要经过这个来换算
def round_to_next(val, step):
    return val - (val % step) + (step if val % step != 0 else 0)


# 重新计算价格精度 输入价格精度起步，并提供价格精度
# def round_price(price, symbol, r2n=None, pp=None):
#     if r2n:
#         if symbol in r2n.keys():
#             price = round_to_next(symbol, price)
#     return round(price, pp[symbol])


# 该币种最小价格波动百分比
def price_min_change(price, symbol, pp):
    return ((0.1 ** pp[symbol]) / price * 1.05) * 100


# 币数量转换成张
def q_to_z(qty, symbol, qty_precision):
    return int(qty / qty_precision[symbol])


# qty precision导入对冲交易所的qty_precision换算成下单币数量
def z_to_q(qty, symbol, qp1, qp2):
    return qp2(qty * qp1[symbol], symbol)


# 导入其他交易所的张数换算来切换成对方交易所的张数
def z_to_z(qty, symbol, qp1, q2z):
    return q2z(qty * qp1[symbol], symbol)


# change to qty
def u_2_qty(symbol, qty, price, qp):
    return round(qty / price, qp[symbol])


# 获取止损止盈价格
def condition_price(side, price, leverage=1):
    if side.lower() == 'buy':
        sl = price - (price * (1 / leverage * 0.7))
        tp = price + (price * (1 / leverage * 0.75))

    else:
        sl = price + (price * (1 / leverage * 0.7))
        tp = price - (price * (1 / leverage * 0.75))
    return sl, tp


# 买卖方向互换
def reverse_side(side):
    if side.lower() == 'buy':
        return 'Sell'
    else:
        return 'Buy'


# 对价格重新计算
def recalculate_price(price, side, mt=0):
    if mt < 8:
        if side == 'Buy':
            price = price * (1 + 0.0005 * mt)
        else:
            price = price * (1 - 0.0005 * mt)

        return price
    else:
        return price


# 发送微信消息
def send_message(user, content):
    # print('message not use')
    try:
        url = 'https://sctapi.ftqq.com/SCT28434TVLJWdPjQnZMY0GOffn5Aa5ki.send'
        params = {'title': user, 'desp': content}
        params = urllib.parse.urlencode(params)
        response = requests.get(url, params=params)
    except Exception as e:
        print('发送消息异常', e)
        send_message(user, content)


# loguru获取BUG
def async_catch(func):
    @wraps(func)
    async def wrapped(self, *arg, **kwargs):
        if self.logger:
            with self.logger.catch():
                return await func(self, *arg, **kwargs)
        else:
            return await func(self, *arg, **kwargs)

    return wrapped


def catch(func):
    def wrapped(self, *arg, **kwargs):
        if self.logger:
            with self.logger.catch():
                return func(self, *arg, **kwargs)
        else:
            return func(self, *arg, **kwargs)

    return wrapped


def min_price_change(symbol, price, side, pp):
    if side.lower == 'buy':
        return round_price(price - (0.1 ** pp[symbol]), symbol,  pp)
    else:
        return round_price(price + (0.1 ** pp[symbol]), symbol, pp)



