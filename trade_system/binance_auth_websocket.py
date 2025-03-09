import websocket
import threading
from binance_auth import *
from precision import *
import pandas
import json


class BinanceAuthWebsocket(BinanceAuth):
    def __init__(self, symbols, key=None, secret=None, proxy=False, http_proxy=None, port=None, log=None, leverage=None,
                 symbol_leverage=None):

        BinanceAuth.__init__(self, key=key, secret=secret, proxy=proxy, http_proxy=http_proxy, port=port,
                             log=log, symbols=symbols)
        self.new_position_data = dict((x, False) for x in self.symbols)
        self.logger = log
        self.symbols = symbols
        self.leverage = leverage
        self.symbol_leverage = dict((x,self.leverage) for x in self.symbols)
        self.listen = self.listen_key()
        # 已执行的止损订单
        self.executed_stop_order = {}
        self.ws = websocket.WebSocketApp(f'wss://fstream.binance.com/ws/{self.listen}',
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         on_open=self.on_open,
                                         on_ping=self.on_ping,
                                         )

        self.wst = threading.Thread(target=self.start_websocket, args=())
        self.wst.daemon = True
        self.wst.start()

        self.rs = threading.Thread(target=self.refresh_connect, args=())
        self.rs.daemon = True
        self.rs.start()

    def on_ping(self, ws,msg):
        self.ws.sock.pong()

    def start_websocket(self):
        while True:
            if self.proxy:
                self.ws.run_forever(http_proxy_host=self.http_porxy, http_proxy_port=self.port, ping_interval=5,proxy_type='http')
            else:
                self.ws.run_forever()

    def refresh_connect(self):
        while True:
            url = '/fapi/v1/listenKey'
            response = self.send_signed_request('POST', url)
            time.sleep(1200)

    def on_error(self, ws,msg):
        print(msg)
        print('binance websocket error', msg)

    def on_close(self, ws,close_status_code,closed_reason):
        print(ws,close_status_code,closed_reason)
        print("### binance websocket closed ###")


    def on_open(self, ws):
        self.balances = self.get_balance()
        self.positions = self.get_positions()
        if self.leverage:
            for symbol in self.symbols:
                self.change_leverage(leverage=self.leverage, symbol=symbol)
                # 改为单向持仓
                self.change_margin_type(symbol)
        else:
            for k, v in self.symbol_leverage.items():
                self.change_leverage(k, leverage=v)

        self.change_dual_side()
        self.logger.success('Binance Websocket Start')

    def on_message(self, ws, message):
        message = json.loads(message)
        if 'e' in message.keys():
            self.parse_update(message)

    # 解析更新数据
    def parse_update(self, message):
        # 追加保证金解析
        if message['e'] == 'MARGIN_CALL':
            for x in message['p']:
                x['timesamp'] = pd.to_datetime(message['E'], unit='ms')


        # 账户数据更新解析
        elif message['e'] == 'ACCOUNT_UPDATE':
            balances = {}
            upnl = 0
            # {交易所{币种：{总量，可用总量}}}
            for x in message['a']['B']:
                balances[x['a']] = {
                    'balance': float(x['wb']),
                    'available': float(x['cw'])
                }
            # {交易所：{交易对：{交易币种，持仓方向，持仓数量，价格，持仓价值，浮动盈亏，浮动盈亏比例}}}
            for x in message['a']['P']:
                if abs(float(x['pa'])) == 0:
                    self.positions.pop(x['s'][:-4])

                else:
                    self.positions[x['s'][:-4]] = {
                        'price': float(x['ep']),
                        'side': 'Buy' if float(x['pa']) > 0 else 'Sell',
                        'qty': abs(float(x['pa']))
                    }
                    upnl += float(x['up'])
                self.new_position_data[x['s'][:-4]] = True
                self.logger.info(f'当前持仓:{self.positions}')

            balances['USDT']['upnl'] = upnl
            self.balances = balances
            return {'type': 'account_update', 'data': {'balances': balances, 'positions': self.positions}}

        elif message['e'] == 'ORDER_TRADE_UPDATE':
            # {交易所:{ID：{交易对，交易币种，创建时间，持仓方向，价格，数量，已成交数量}}}
            x = message['o']
            if x['i'] in self.orders.keys():
                self.orders[x['i']]['cqty'] = self.orders[x['i']]['cqty'] + float(x['l'])
                self.orders[x['i']]['status'] = x['X']
            else:
                self.orders[x['i']] = {
                    'symbol': x['s'],
                    'timestamp': pd.to_datetime(message['E'], unit='ms'),
                    'side': x['S'].upper(),
                    'price': float(x['p']),
                    'qty': float(x['q']),
                    'cqty': float(x['z']),
                    'status': x['X'],
                    'stop_price': float(x['sp'])
                }
            if x['o'] == 'LIQUIDATION':
                print('币安强平!!!!!!!!!!!!')
                print(message)
                x = message['o']
                if x['s'][:-4] in self.sys_risk:
                    pass
                else:
                    self.sys_risk.append(x['s'][:-4])
            elif x['o'] == 'STOP':
                x = message['o']
                self.executed_stop_order[x['i']] = x

            elif x['o'] in ['TAKE_PROFIT_MARKET', 'STOP_MARKET'] and x['x'] == 'EXPIRED':
                print('币安止盈止损触发!')
                print(message)
                x = message['o']
                if x['s'][:-4] in self.sys_risk:
                    pass
                else:
                    self.sys_risk.append(x['s'][:-4])

if __name__ == '__main__':
    import loguru as logger
    import sys

    logger.add(sys.stderr, level='INFO')
    client = BinanceAuthWebsocket(symbols=['BTCUSDT'], leverage=2, proxy=True, key='',
                             secret='',log=logger,
                                  http_proxy='127.0.0.1', port=7890)