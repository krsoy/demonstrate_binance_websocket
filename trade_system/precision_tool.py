from .precision import *

perp_price_precision, perp_qty_precision = perp_info()
print('precision initialized')


def round_quantity(exchange, symbol, n):
    precision = perp_qty_precision[exchange][symbol]
    if exchange in ['gate']:
        return int(n)
    return round(n, precision)
def carry_round(num,precision):
    if isinstance(num, int):
        return num
    else:
        whole, decimal = str(num).split('.')

        if len(decimal)<precision:
            return float(str(num))


        if int(decimal[-1]) > 5:
            new_decimal = str(int(decimal[:-1]) + 1) if len(decimal)>1 else str(int(decimal) + 1)
            if len(new_decimal) > len(decimal[:-1]):
                return int(whole) + 1
            else:
                return float(f"{whole}.{new_decimal}")

        elif int(decimal[-1]) < 5:
            new_decimal = decimal[:-1] + "0"
            return float(f"{whole}.{new_decimal}")
        else:
            return float(str(num))

def round_price(exchange, symbol, n):
    precision = perp_price_precision[exchange][symbol]
    if exchange in round5:

        if symbol in round5[exchange]:

            val = round(n, precision)
            return carry_round(val,precision)

    return round(n, precision)