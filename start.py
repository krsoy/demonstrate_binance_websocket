import time

from binance import *

symbols = ['BTC', 'ETH', 'BCH', 'XRP', 'EOS', 'LTC', 'TRX', 'ETC', 'LINK', 'XLM', 'ADA', 'XMR', 'DASH',
                       'ZEC', 'XTZ', 'BNB', 'ATOM', 'ONT', 'IOTA', 'BAT', 'VET', 'NEO', 'QTUM', 'IOST', 'THETA', 'ALGO',
                       'ZIL', 'KNC', 'ZRX', 'COMP', 'OMG', 'DOGE', 'SXP', 'KAVA', 'BAND', 'RLC', 'WAVES', 'MKR', 'SNX',
                       'DOT', 'DEFI', 'YFI', 'BAL', 'CRV', 'TRB', 'RUNE', 'SUSHI', 'SRM', 'EGLD', 'SOL', 'ICX', 'STORJ',
                       'BLZ', 'UNI', 'AVAX', 'FTM', 'HNT', 'ENJ', 'FLM', 'TOMO', 'REN', 'KSM', 'NEAR', 'AAVE', 'FIL',
                       'RSR', 'LRC', 'MATIC', 'OCEAN', 'CVC', 'BEL', 'CTK', 'AXS', 'ALPHA', 'ZEN', 'SKL', 'GRT',
                       '1INCH', 'CHZ', 'SAND', 'ANKR', 'BTS', 'LIT', 'UNFI', 'REEF', 'RVN', 'SFP', 'XEM', 'COTI', 'CHR',
                       'MANA', 'ALICE', 'HBAR', 'ONE', 'LINA', 'STMX', 'DENT', 'CELR', 'HOT', 'MTL', 'OGN', 'NKN', 'SC',
                       'DGB', '1000SHIB', 'BAKE', 'GTC', 'BTCDOM', 'IOTX', 'AUDIO', 'RAY', 'C98', 'MASK', 'ATA', 'DYDX',
                       '1000XEC', 'GALA', 'CELO', 'AR', 'KLAY', 'ARPA', 'CTSI', 'LPT', 'ENS', 'PEOPLE', 'ANT', 'ROSE',
                       'DUSK', 'FLOW', 'IMX', 'API3', 'GMT', 'APE', 'WOO', 'FTT', 'JASMY', 'DAR', 'GAL', 'OP', 'INJ',
                       'STG', 'FOOTBALL', 'SPELL', 'LDO', 'CVX', 'ICP', 'APT', 'QNT', 'BLUEBIRD',
                       'FET', 'FXS', 'HOOK', 'MAGIC', 'T', 'RNDR', 'HIGH', 'MINA', 'ASTR', 'AGIX', 'PHB', 'GMX', 'CFX',
                       'STX', 'COCOS', 'BNX', 'ACH', 'SSV', 'CKB', 'PERP', 'TRU', 'LQTY', 'USDC', 'ID', 'ARB', 'JOE',
                       'TLM', 'AMB', 'LEVER', 'RDNT', 'HFT', 'XVS', 'BLUR', 'EDU', 'IDEX', 'SUI', '1000PEPE',
                       '1000FLOKI', 'UMA', 'RAD', 'KEY', 'COMBO', 'NMR', 'MAV', 'MDT', 'XVG', 'WLD', 'PENDLE', 'ARKM',
                       'AGLD', 'YGG', 'DODOX', 'BNT', 'OXT', 'SEI', 'CYBER', 'HIFI', 'ARK', 'FRONT', 'GLMR', 'BICO',
                       'STRAX', 'LOOM', 'BIGTIME', 'BOND', 'ORBS', 'STPT', 'WAXP', 'BSV', 'RIF', 'POLYX', 'GAS', 'POWR',
                       'SLP', 'TIA', 'SNT', 'CAKE', 'MEME', 'TWT', 'TOKEN', 'ORDI', 'STEEM', 'BADGER', 'ILV', 'NTRN',
                       'MBL', 'KAS', 'BEAMX', '1000BONK', 'PYTH', 'SUPER', 'USTC', 'ONG', 'ETHW', 'JTO', '1000SATS',
                       'AUCTION', '1000RATS', 'ACE', 'MOVR', 'NFP', 'AI', 'XAI', 'WIF', 'TRUMP']

binance_trade = BinanceTradeStorage(symbols, proxy=True)