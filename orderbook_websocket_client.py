import threading
import asyncio
import ujson as json
import redis.asyncio as redis
import websocket
import time

class OrderBooKClient:
    def __init__(self, name, url,proxy=False):
        self.url = url
        self.name = name
        self.reconnect_num = 0
        self.redis = None
        self.connect_status = True
        self.proxy = proxy
        self.http_proxy ='127.0.0.1'
        self.port = '7899'
        self.websocket = websocket.WebSocketApp(self.url,
                                                on_message=self.on_message,
                                                on_error=self.on_error,
                                                on_close=self.on_close,
                                                on_open=self.on_open,

                                                )

        self.wst = threading.Thread(target=self.start_websocket, args=())
        self.wst.daemon = True
        self.wst.start()


    def start_websocket(self):
        while True:
            if self.proxy:
                print('proxy websocket start',self.http_proxy,self.port)
                self.websocket.run_forever(http_proxy_host=self.http_proxy, http_proxy_port=self.port,
                                           skip_utf8_validation=True,proxy_type='http')
            else:
                self.websocket.run_forever()

    def auto_reconnect(self):
        while True:
            self.connect_status = False

    def callback(self, message):
        print(f"Received: {message}")

    def send(self, data):
        self.websocket.send(data)

    def subscribe(self,data):
        self.send(data)

    def unsubscribe(self, data):
        self.send(data)

    def on_open(self,ws):
        pass

    def on_close(self,ws, close_status_code, close_msg):
        print(close_msg)

    def on_error(self,ws, error):
        print(error)

    def on_message(self,ws, message):
        print(f"Received: {message}")
        pass


