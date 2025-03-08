import json as send_json

from orderbook_websocket_client import *
import time


class BinanceOrderBook(OrderBooKClient):

    def __init__(self, symbols,proxy=False,is_perp=True):
        OrderBooKClient.__init__(self,
                                 name='binance',
                                 url='wss://fstream.binance.com/ws' if is_perp else 'wss://stream.binance.com:9443/ws',
                                    proxy=proxy,
                                 )

        self.symbols = symbols
        self.latency = []
        self.n = 0
        self.bd = {}
        self.sd = {}
        self.ts = {}


    def on_open(self,ws):
        print('binance orderbook starting')
        content = {
            "method": "SUBSCRIBE",
            "params":
                [
                    f"{s.lower()}usdt@kline_1m" for s in self.symbols
                ],
            "id": 1
        }
        print('binance orderbook started')
        self.send(send_json.dumps(content))

    def on_message(self,ws, message):
        message = json.loads(message)
        try:
            print(time.time()-int(message['E'])/1000)

        except:
            pass



if __name__ == "__main__":
    symbols = ['BTC', 'ETH', 'BCH', 'XRP', 'EOS', 'LTC', 'TRX', 'ETC', 'LINK', 'XLM', 'ADA', 'XMR', 'DASH', 'ZEC',
               'XTZ', 'BNB', 'ATOM', 'ONT', 'IOTA', 'BAT', 'VET', 'NEO', 'QTUM', 'IOST', 'THETA', 'ALGO', 'ZIL', 'KNC',
               'ZRX', 'COMP', 'OMG', 'DOGE', 'SXP', 'KAVA', 'BAND', 'RLC', 'WAVES', 'MKR', 'SNX', 'DOT', 'DEFI', 'YFI',
               'BAL', 'CRV', 'TRB', 'RUNE', 'SUSHI', 'SRM', 'EGLD', 'SOL', 'ICX', 'STORJ', 'BLZ', 'UNI', 'AVAX', 'FTM',
               'HNT', 'ENJ', 'FLM', 'TOMO', 'REN', 'KSM', 'NEAR', 'AAVE', 'FIL', 'RSR', 'LRC', 'MATIC', 'OCEAN', 'CVC',
               'BEL', 'CTK', 'AXS', 'ALPHA', 'ZEN', 'SKL', 'GRT', '1INCH', 'CHZ', 'SAND', 'ANKR', 'BTS', 'LIT', 'UNFI',
               'REEF', 'RVN', 'SFP', 'XEM', 'COTI', 'CHR', 'MANA', 'ALICE', 'HBAR', 'ONE', 'LINA', 'STMX', 'DENT',
               'CELR', 'HOT', 'MTL', 'OGN', 'NKN', 'SC', 'DGB', '1000SHIB', 'BAKE', 'GTC', 'BTCDOM', 'IOTX', 'AUDIO',
               'RAY', 'C98', 'MASK', 'ATA', 'DYDX', '1000XEC', 'GALA', 'CELO', 'AR', 'KLAY', 'ARPA', 'CTSI', 'LPT',
               'ENS', 'PEOPLE', 'ANT', 'ROSE', 'DUSK', 'FLOW', 'IMX', 'API3', 'GMT', 'APE', 'WOO', 'FTT', 'JASMY',
               'DAR', 'GAL', 'OP', 'INJ', 'STG', 'FOOTBALL', 'SPELL', '1000LUNC', 'LUNA2', 'LDO', 'CVX', 'ICP', 'APT',
               'QNT', 'BLUEBIRD', 'FET', 'FXS', 'HOOK', 'MAGIC', 'T', 'RNDR', 'HIGH', 'MINA', 'ASTR', 'AGIX', 'PHB',
               'GMX', 'CFX', 'STX', 'COCOS', 'BNX', 'ACH', 'SSV', 'CKB', 'PERP', 'TRU', 'LQTY', 'USDC', 'ID', 'ARB',
               'JOE', 'TLM', 'AMB', 'LEVER', 'RDNT', 'HFT', 'XVS', 'BLUR', 'EDU', 'IDEX', 'SUI', '1000PEPE',
               '1000FLOKI', 'UMA', 'RAD', 'KEY', 'COMBO']

    t = BinanceOrderBook(symbols=symbols,proxy=True)
    # keep code running don't quit

