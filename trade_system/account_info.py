# -*- coding: utf-8 -*-
# https://www.linkedin.com/in/chenghao1990/

class Account:
    def __init__(self, exchange_name, round_price, round_qty,key, secret, password=None, leverage=1, dual_side=False):
        self.name = exchange_name
        # 所有订单
        self.orders = {}
        # 持仓
        self.positions = {}
        # 钱包
        self.balances = {}
        # 自动减仓
        self.auto_deleverage = {}
        # 强平
        self.sys_risk = []
        # 交易所修正价格功能 def
        self.round_price = round_price
        # 交易所修正数量功能 def
        self.round_qty = round_qty
        # 密码
        self.password = password
        # 杠杆倍数
        self.leverage = leverage
        # 当前挂单开仓
        self.current_post_order = {}
        # 当前止损单
        self.current_stop = {}
        # 当前止盈单
        self.current_profit = {}
        # 当前追踪止损单
        self.current_trailing_order = {}
        # 钱包
        self.balance = {}
        self.key = key
        self.secret = secret
        # 是否允许双向持仓
        self.dual_side = dual_side

        self.take_profit_switch = False
        self.stop_loss_switch = False

        self.take_profit_number = 0
        self.stop_loss_number = 0
        self.position_marked = {}

    def __str__(self):
        return self.name

    def pre_cancel_condition_order(self,symbol):
        # 取消condition order前的步骤，删除orders和current orders里边的数据，释放内存
        if symbol in self.current_post_order.keys():
            if self.current_post_order[symbol] in self.orders.keys():
                self.orders.pop(self.current_post_order[symbol])
            self.current_post_order.pop(symbol)

        if symbol in self.current_profit.keys():
            if self.current_profit[symbol] in self.orders.keys():
                self.orders.pop(self.current_profit[symbol])
            self.current_profit.pop(symbol)
