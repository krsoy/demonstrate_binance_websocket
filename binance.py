import sqlite3
import threading
import time
import json
import gzip
import datetime
from binance_orderbook import *
# Assuming BinanceOrderBook is defined elsewhere
# from your_module import BinanceOrderBook


class BinanceTradeStorage(BinanceOrderBook):
    def __init__(self, symbols, proxy=False, db_file='trade.db', is_perp=True):
        self.symbols = symbols
        self.db_file = db_file
        self.trade_buffer = dict((x, []) for x in symbols)
        self.buffer_lock = threading.Lock()

        # Set up SQLite database and tables
        self.setup_database()

        # Background thread that flushes buffer every minute
        self.stop_event = threading.Event()
        self.flush_thread = threading.Thread(target=self.flush_data_periodically, daemon=True)
        self.flush_thread.start()
        super().__init__(symbols, proxy=proxy, is_perp=is_perp)

    def setup_database(self):
        """Create SQLite tables for each symbol."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            for symbol in self.symbols:
                table_name = f'binance_{symbol.lower()}'
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        compressed_trades BLOB NOT NULL
                    )
                ''')
            conn.commit()

    def on_open(self, ws):
        content = {
            "method": "SUBSCRIBE",
            "params": [f"{s.lower()}usdt@trade" for s in self.symbols],
            "id": 1
        }
        print('binance trade start', content)
        self.send(json.dumps(content))

    def on_close(self, ws, close_status_code, close_msg):
        """On close, signal the flush thread to stop and do a final flush."""
        print('WebSocket closed, flushing final data...', close_msg)
        self.stop_event.set()

        with self.buffer_lock:
            for symbol, trades in self.trade_buffer.items():
                if not trades:
                    continue
                compressed_trades = self.compress_trades(trades)
                self.insert_data(symbol, compressed_trades)
            self.trade_buffer = dict((x, []) for x in self.symbols)

        self.flush_thread.join()

    def on_message(self, ws, message):
        try:
            message = json.loads(message)
            if 'id' in message:
                return

            symbol = message['s'][:-4]
            data = {
                'price': float(message['p']),
                'qty': float(message['q']),
                'timestamp': message['T'] / 1000,
                'is_buyer_maker': message['m'],
                'order_id': message['t']
            }
            with self.buffer_lock:
                self.trade_buffer[symbol].append(data)
        except Exception as e:
            print(e, message)

    def flush_data_periodically(self):
        """Runs in a background thread to flush the buffer every 60 seconds."""
        while not self.stop_event.is_set():
            time.sleep(60)

            with self.buffer_lock:
                trades_to_flush = self.trade_buffer
                self.trade_buffer = dict((x, []) for x in self.symbols)

            for symbol, trades in trades_to_flush.items():
                if not trades:
                    continue
                try:
                    compressed_trades = self.compress_trades(trades)
                    self.insert_data(symbol, compressed_trades)
                    print('flushed', symbol)
                except Exception as e:
                    print('insert error:', e)

    def insert_data(self, symbol, compressed_trades):
        """Insert compressed trades into SQLite."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            timestamp = datetime.datetime.utcfromtimestamp(time.time()).isoformat()
            table_name = f'binance_{symbol.lower()}'
            cursor.execute(f'''
                INSERT INTO {table_name} (timestamp, compressed_trades)
                VALUES (?, ?)
            ''', (timestamp, compressed_trades))
            conn.commit()

    def compress_trades(self, trade_list):
        """Compress a list of trade dictionaries into bytes."""
        data_str = json.dumps(trade_list)
        data_bytes = data_str.encode('utf-8')
        compressed = gzip.compress(data_bytes)
        return compressed

# Example usage (uncomment to test):
# symbols = ["BTC", "ETH"]
# trade_storage = BinanceTradeStorage(symbols)