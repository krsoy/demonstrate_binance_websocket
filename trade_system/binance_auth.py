import hmac
import time
import hashlib
from urllib.parse import urlencode, quote

import requests

from Exchanges.utils import *
from Exchanges.framework import *
import pandas as pd
import re


class BinanceAuth(Account):

    def __init__(self, symbols, key=None, secret=None, proxy=False, http_proxy=None, port=None, log=None):
        Account.__init__(self, exchange_name='binance', round_price=binance_rp, round_qty=float_qty,key=key,secret=secret)
        self.symbols = symbols
        self.logger = log
        self.unity_qty = lambda x, y: x
        self.self_qty = lambda x, y: x
        # 日志接口
        self.key = key
        self.secret = secret
        # 代理设置
        self.proxy = proxy
        self.http_porxy = http_proxy
        self.port = port
        if proxy:
            self.proxies = {
                'https': 'https://localhost:7890',
                'http': 'http://localhost:7890'
            }
        else:
            self.proxies = None
        # 基础请求链接
        self.base = 'https://fapi.binance.com'

    def hashing(self, query):
        return hmac.new(self.secret.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()

    def listen_key(self):
        url = '/fapi/v1/listenKey'

        response = self.send_signed_request('POST', url, )
        return response['listenKey']

    def timestamp(self):
        return int(time.time() * 1000 + 1)

    def dispatch_request(self, http_method):
        session = requests.Session()
        session.headers.update({
            'Content-Type': 'application/json;charset=utf-8',
            'X-MBX-APIKEY': self.key
        })

        while True:
            try:
                result = {
                    'GET': session.get,
                    'DELETE': session.delete,
                    'PUT': session.put,
                    'POST': session.post,
                }.get(http_method, 'GET')

                return result
            except Exception as e:
                print('binance 请求失败')
                print(e)
                time.sleep(5)

    @catch
    def send_public_request(self, url_path, payload={}):
        query_string = urlencode(payload, True)
        url = self.base + url_path
        if query_string:
            url = url + '?' + query_string
        print("{}".format(url))
        response = self.dispatch_request('GET')(url=url, proxies=self.proxies)

        return response.json()

    @catch
    def send_signed_request(self, http_method, url_path, payload={}, base=None):
        if base:
            base = base
        else:
            base = self.base
        query_string = urlencode(payload)
        query_string = query_string.replace('%27', '%22')

        if query_string:
            query_string = "{}&timestamp={}".format(query_string, self.timestamp())
        else:
            query_string = 'timestamp={}'.format(self.timestamp())

        url = base + url_path + '?' + query_string + '&signature=' + self.hashing(query_string)
        params = {'url': url, 'params': {}, 'proxies': self.proxies}
        while True:
            try:
                response = self.dispatch_request(http_method)(**params)
                if response.status_code not in [200, 400]:
                    print('币安 post 请求失败！')
                    print('代码', response.status_code)
                    print('内容', response.json())
                    return {'code': 'shutdown', 'content': f'币安返回异常，风控启动:{response.json()}'}
                else:
                    return response.json()
            except Exception as e:
                print('币安请求失败')

    def get_balance(self):
        balances = {}
        url = '/fapi/v2/account'
        data = self.send_signed_request('GET', url)
        balances['USDT'] = {
            'balance': float(data['totalWalletBalance']),
            'available': float(data['availableBalance']),
            'upnl': float(data['totalUnrealizedProfit'])
        }
        return balances

    def get_uid(self):
        url = '/fapi/v2/balance'
        data = self.send_signed_request('GET', url)
        print(data[0]['accountAlias'])

    def get_history_order(self, symbol, order_id):
        url = '/fapi/v1/order'
        payload = {
            'symbol': f'{symbol}USDT',
            'orderId': order_id,
        }
        response = self.send_signed_request('GET', url, payload=payload)
        return response

    def get_positions(self):
        positions = {}
        url = '/fapi/v2/positionRisk'
        data = self.send_signed_request('GET', url, payload={'timestamp': self.timestamp()})
        try:
            if data:
                for d in data:
                    if 'positionAmt' in d.keys():
                        if float(d['positionAmt']) != 0:
                            if float(d['positionAmt']) > 0:
                                side = 'Buy'
                            else:
                                side = 'Sell'
                            positions[d['symbol'][:-4]] = {
                                'qty': abs(float(d['positionAmt'])),
                                'side': side,
                                'price': float(d['entryPrice']),
                                'upnl': round((float(d['unRealizedProfit'])),2)
                            }
                self.positions.update(positions)
                return positions
        except Exception as e:
            print(e)
            print(data)
            return {}

    def new_order(self, symbol, side, qty=None, price=None, liquidation=False, _type='MARKET', tif=None):
        if 'USDT' not in symbol:
            symbol += 'USDT'

        url = '/fapi/v1/order'

        params = {
            'symbol': symbol,
            'newClientOrderId':f'x-sQ6aNTbG{int(time.time()*1000000)}',
            'side': side.upper(),
            'type': _type,
            'quantity': qty,
            'reduceOnly': 'true' if liquidation else 'false'
        }
        if tif:
            params.update({'timeInForce': tif})

        if price:
            params.update({'price': price})
        response = self.send_signed_request('POST', url, payload=params)

        return response

    def stop_loss_order(self, symbol, side, price):
        if 'USDT' not in symbol:
            symbol += 'USDT'
        url = '/fapi/v1/order'
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': 'STOP_MARKET',
            'closePosition': True,
            'stopPrice': price,
            'newClientOrderId': f'x-sQ6aNTbG{int(time.time() * 1000000)}',
        }
        response = self.send_signed_request('POST', url, payload=params)

        return response

    def take_profit_order(self, symbol, side, price):
        url = '/fapi/v1/order'
        if 'USDT' not in symbol:
            symbol += 'USDT'
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': 'TAKE_PROFIT_MARKET',
            'closePosition': True,
            'stopPrice': price,
            'newClientOrderId': f'x-sQ6aNTbG{int(time.time() * 1000000)}',

        }
        response = self.send_signed_request('POST', url, payload=params)
        return response

    def trailing_stop_order(self, symbol, side, qty, rate):
        if 'USDT' not in symbol:
            symbol += 'USDT'
        url = '/fapi/v1/order'
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': 'TRAILING_STOP_MARKET',
            'quantity': qty,
            'callbackRate': rate,
        }
        response = self.send_signed_request('POST', url, payload=params)
        return response

    def new_condition_order(self,symbol,side,slp,tpp):
        self.take_profit_order(symbol,side,tpp)
        self.stop_loss_order(symbol,side,slp)
    # 套利用
    def update_dual_condition(self, leverage=1):
        for symbol in self.positions:
            price = self.positions[symbol]['price']
            side = self.positions[symbol]['side']
            # stop loss price
            slp, tpp = condition_price(side, price, leverage=leverage)
            self.cancel_all_condition_order_by_symbol(symbol)
            self.new_condition_order(symbol, reverse_side(side),slp, tpp)

    # 自定义用
    def update_cta_condition(self,symbol,side,price):
        return self.stop_loss_order(symbol, side, price)



    def stop_order(self, symbol, side, qty):
        if 'USDT' not in symbol:
            symbol += 'USDT'
        url = '/fapi/v1/order'
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': 'MARKET',
            'quantity': qty,
            'reduceOnly': 'true',
            'newClientOrderId': f'x-sQ6aNTbG{int(time.time() * 1000000)}',
        }

        response = self.send_signed_request('POST', url, payload=params)
        return response

    def cancel_all_order_by_symbol(self, symbol):
        if 'USDT' not in symbol:
            symbol += 'USDT'
        url = '/fapi/v1/allOpenOrders'
        params = {'symbol': symbol}
        response = self.send_signed_request('DELETE', url, payload=params)
        return response

    def cancel_all_condition_order_by_symbol(self, symbol):
        self.pre_cancel_condition_order(symbol)
        if 'USDT' not in symbol:
            symbol += 'USDT'
        url = '/fapi/v1/allOpenOrders'
        params = {'symbol': symbol}
        response = self.send_signed_request('DELETE', url, payload=params)
        return response

    def delete_order(self, symbol, order_id):
        symbol = symbol.upper()
        if 'USDT' not in symbol:
            symbol += 'USDT'
        url = '/fapi/v1/order'
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        response = self.send_signed_request('DELETE', url, payload=params)
        return response

    def open_orders(self):
        url = '/fapi/v1/openOrders'
        response = self.send_signed_request('GET', url)
        return response

    def restore_condition_order(self):
        data = self.open_orders()
        self.restore_order_details(data)
        for d in data:
            if d['symbol'][:-4] in self.positions.keys():
                if d['type'] == 'STOP_MARKET':
                    self.current_stop[d['symbol'][:-4]] = d['orderId']
                elif d['type'] == 'TAKE_PROFIT_MARKET':
                    self.current_profit[d['symbol'][:-4]] = d['orderId']
            else:
                self.cancel_all_condition_order_by_symbol(d['symbol'][:-4])

    def restore_order_details(self, data):

        orders = {}
        if type(data) == list:
            for x in data:
                orders[x['orderId']] = {
                    'symbol': x['symbol'],
                    'timestamp': x['time'] / 1000,
                    'side': x['side'].upper(),
                    'price': float(x['price']),
                    'qty': float(x['origQty']),
                    'cqty': float(x['executedQty']),
                    'status': x['status'],
                    'stop_price': float(x['stopPrice'])

                }
        else:
            x = data
            orders[x['orderId']] = {
                'symbol': x['symbol'],
                'timestamp': x['time'] / 1000,
                'side': x['side'].upper(),
                'price': float(x['price']),
                'qty': float(x['origQty']),
                'cqty': float(x['executedQty']),
                'status': x['status'],
                'stop_price': float(x['stopPrice'])

            }
        self.orders.update(orders)
        return orders

    def change_dual_side(self):
        url = '/fapi/v1/positionSide/dual'
        params = {'dualSidePosition': 'false'}
        response = self.send_signed_request('POST', url, payload=params)
        return response

    def check_dual_side(self):
        url = '/fapi/v1/positionSide/dual'
        response = self.send_signed_request('GET', url, payload={})
        return response

    def change_margin_type(self, symbol):
        if 'USDT' not in symbol:
            symbol += 'USDT'
        url = '/fapi/v1/marginType'
        params = {'symbol': symbol, 'marginType': 'ISOLATED'}
        self.send_signed_request('POST', url, payload=params)

    def set_margin_type(self, symbol):
        url = '/fapi/v1/marginType'
        params = {'symbol': symbol, 'marginType': 'ISOLATED'}
        return self.send_signed_request('POST', url, payload=params)

    def change_leverage(self, symbol, leverage=1):
        if 'USDT' not in symbol:
            symbol += 'USDT'
        url = '/fapi/v1/leverage'
        params = {
            'symbol': f'{symbol.upper()}',
            'leverage': leverage,
        }
        response = self.send_signed_request('POST', url, payload=params)
        return response

    def set_leverage(self, symbol, leverage):
        if 'USDT' not in symbol:
            symbol += 'USDT'
        url = '/fapi/v1/leverage'
        params = {
            'symbol': f'{symbol}USDT',
            'leverage': leverage,
        }
        response = self.send_signed_request('POST', url, payload=params)
        return response

    def close_all_position(self):
        for key in list(self.positions.keys()):
            if self.positions[key]['side'] == 'Buy':
                side = 'Sell'
            else:
                side = 'Buy'
            print('开始平仓', key)
            response = self.stop_order(symbol=key, side=side, qty=self.positions[key]['qty'])
            print(response)
            self.cancel_all_order_by_symbol(key)

    def get_position_qty(self, symbol):
        url = '/fapi/v2/positionRisk'
        data = self.send_signed_request('GET', url, payload={'timestamp': self.timestamp()})

        if data:
            for d in data:
                if d['symbol'] == f'{symbol}USDT':
                    return d

        return None

    def get_spot_snapshot(self):
        url = '/sapi/v1/accountSnapshot'
        payload = {'type':'SPOT','startTime':1651481308000,'limit':30}
        data = self.send_signed_request(http_method='GET', url_path=url, payload=payload, base='https://api.binance.com')
        return data

    def sys_risk_execute(self, symbol):
        if symbol in self.positions.keys():
            if self.positions[symbol]['side'] == 'Buy':
                side = 'Sell'
            else:
                side = 'Buy'
            print('币安开始强制平仓', symbol)
            response = self.stop_order(symbol=symbol, side=side, qty=self.positions[symbol]['qty'])
            print(response)
            return response

    def contract_info(self):
        url = '/fapi/v1/exchangeInfo'
        _data = requests.get(self.base+url,proxies=self.proxies).json()
        print(_data)
        _price_precision = {}
        _quantity_precision = {}
        for _d in _data['symbols']:
            if _d['contractType'] == 'PERPETUAL' and 'USDT' in _d['symbol']:
                _quantity_precision[_d['symbol'][:-4]] = _d['filters'][1]['stepSize']
                _price_precision[_d['symbol'][:-4]] = _d['filters'][0]['tickSize']
                # ticksize is 0.1~0.0000100 string, convert to int for round, ignore 0 behind 1
                _price_precision[_d['symbol'][:-4]] = len(re.findall(r'0{}1',_price_precision[_d['symbol'][:-4]])[0])
        return _price_precision,_quantity_precision

    # 主动取资金费率
    def funding_rate(self):
        url = '/fapi/v1/premiumIndex'
        data = {}
        result = requests.get(self.base+url).json()
        for r in result:
            if float(r['lastFundingRate']) == 0:
                data[r['symbol'][:-4]] = 0.00001
            else:
                data[r['symbol'][:-4]] = float(r['lastFundingRate'])
        return data

if __name__ == '__main__':

    binance = BinanceAuth(key='', secret='', proxy=False,symbols=['ETH'])
    # data = binance.get_spot_snapshot()
    print(binance.contract_info())

