import requests
import re
from typing import Dict
round5 = {
    'bitget': ['BTC', 'NEAR', 'EGLD', 'KSM', 'CHZ', 'XMR', 'ROSE', 'MTL', 'AUDIO', 'SXP', 'TRB']
}
def ticksize_to_int(ticksize_str):
    """
    Convert a tick size string like '0.1' or '0.00100' to an integer,
    representing the number of decimal places, ignoring trailing zeros.

    :param ticksize_str: Tick size as a string.
    :return: Integer representing the number of decimal places.
    """
    # Remove trailing zeros and split at the decimal point
    ticksize_str = ticksize_str.rstrip('0')
    if '.' in ticksize_str:
        return len(ticksize_str.split('.')[1])  # Count decimal places
    else:
        return 0  # No decimal point means 0 decimal places

def binance_perp_info():
    url = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
    response = requests.get(url)
    data = response.json()
    _price_precision = {}
    _quantity_precision = {}
    for _d in data['symbols']:
        if _d['contractType'] == 'PERPETUAL' and 'USDT' in _d['symbol']:
            _quantity_precision[_d['symbol'][:-4]] = ticksize_to_int(_d['filters'][1]['stepSize'])
            # ticksize is 0.1~0.0000100 string, convert to int for round, ignore 0 behind 1
            _price_precision[_d['symbol'][:-4]] = ticksize_to_int(_d['filters'][0]['tickSize'])
    return _price_precision, _quantity_precision


def gate_perp_info():
    url = 'https://api.gateio.ws/api/v4/futures/usdt/contracts'
    response = requests.get(url)
    data = response.json()
    _price_precision = {}
    _quantity_precision = {}
    for s in data:
        _price_precision[s['name'][:-5]] = len(re.search('.(.*)', str(s['order_price_round']))[1]) - 1
    for s in data:
        _quantity_precision[s['name'][:-5]] = float(s['quanto_multiplier'])

    return _price_precision, _quantity_precision



def perp_info():
    perp_list = {'binance': binance_perp_info(), 'gate': gate_perp_info()}
    perp_qty_precision = {}
    perp_price_precision = {}
    for exchange,item in perp_list.items():
        perp_qty_precision[exchange] = item[1]
        perp_price_precision[exchange] = item[0]

    return perp_price_precision, perp_qty_precision



if __name__ == '__main__':
    perp_price_precision, perp_qty_precision = perp_info()