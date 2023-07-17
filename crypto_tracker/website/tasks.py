import ccxt
import pandas as pd
from celery import shared_task

@shared_task(bind=True)
def test_func(self):
    #operations here
    for i in range(10):
        print(i)
    return "Done"

@shared_task(bind=True, name="BTCUSDT")
def get_price_change(self, period=86400000, exchange_name='binance', symbol="BTCUSDT"):
    # hour=3600000, day=86400000, week=604800000, month(30days)=2592000000, year=31536000000
    exchange = getattr(ccxt, exchange_name)()
    current_price = exchange.fetch_ohlcv(symbol, limit=2)[0]
    period_price = exchange.fetch_ohlcv(symbol, timeframe='1h', since=current_price[0] - period, limit=1)[0][4]
    result = current_price[4] / (period_price * 0.01)
    task_id = self.request.id
    return {'result': f"{(result - 100):.2f}", 'task_id': task_id}


# def get_index_prices():
#     context = {
#         'articles': articles,
#         'room_name': 'track',
#         'BTCUSDT': {'current': BTCUSDT, 
#                     '1h': BTCUSDT_24h_result
#                     '24h': get_price_change.delay(period=86400000, symbol='BTCUSDT'),
#                     '7d': get_price_change.delay(period=604800000, symbol='BTCUSDT'),
#                     '30d': get_price_change.delay(period=2592000000, symbol='BTCUSDT'),
#                     '365d': get_price_change.delay(period=31536000000, symbol='BTCUSDT')
#                     },
#         'ETHUSDT': {'current': ETHUSDT, 
#                     '1h': get_price_change.delay(period=3600000, symbol='ETHUSDT'), #period=3600000, symbol='ETHUSDT'
#                     '24h': get_price_change.delay(period=86400000, symbol='ETHUSDT'), #period=86400000, symbol='ETHUSDT'
#                     '7d': get_price_change.delay(period=604800000, symbol='ETHUSDT'), #period=604800000, symbol='ETHUSDT'
#                     '30d': get_price_change.delay(period=2592000000, symbol='ETHUSDT'), #period=2592000000, symbol='ETHUSDT'
#                     '365d': get_price_change.delay(period=31536000000, symbol='ETHUSDT') #period=31536000000, symbol='ETHUSDT'
#                     },
#         'BUSDUSDT': {'current': BUSDUSDT, 
#                     '1h': get_price_change.delay(period=3600000, symbol='BUSDUSDT'),
#                     '24h': get_price_change.delay(period=86400000, symbol='BUSDUSDT'),
#                     '7d': get_price_change.delay(period=604800000, symbol='BUSDUSDT'),
#                     '30d': get_price_change.delay(period=2592000000, symbol='BUSDUSDT'),
#                     '365d': get_price_change.delay(period=31536000000, symbol='BUSDUSDT')
#                     },
#         'BNBUSDT': {'current': BNBUSDT, 
#                     '1h': get_price_change.delay(period=3600000, symbol='BNBUSDT'),
#                     '24h': get_price_change.delay(period=86400000, symbol='BNBUSDT'),
#                     '7d': get_price_change.delay(period=604800000, symbol='BNBUSDT'),
#                     '30d': get_price_change.delay(period=2592000000, symbol='BNBUSDT'),
#                     '365d': get_price_change.delay(period=31536000000, symbol='BNBUSDT')},
#         'USDCUSDT': {'current': USDCUSDT, 
#                     '1h': get_price_change.delay(period=3600000, symbol='USDCUSDT'),
#                     '24h': get_price_change.delay(period=86400000, symbol='USDCUSDT'),
#                     '7d': get_price_change.delay(period=604800000, symbol='USDCUSDT'),
#                     '30d': get_price_change.delay(period=2592000000, symbol='USDCUSDT'),
#                     '365d': get_price_change.delay(period=31536000000, symbol='USDCUSDT')},
#     }