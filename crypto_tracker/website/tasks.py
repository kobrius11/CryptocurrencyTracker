import ccxt
import pandas as pd
from celery import shared_task, Task

@shared_task(bind=True)
def test_func(self):
    #operations here
    for i in range(10):
        print(i)
    return "Done"

@shared_task
def get_price_change(period=86400000, exchange_name='binance', symbol="BTCUSDT"):
    # hour=3600000, day=86400000, week=604800000, month(30days)=2592000000, year=31536000000
    exchange = getattr(ccxt, exchange_name)()
    current_price = exchange.fetch_ohlcv(symbol, limit=2)[0]
    period_price = exchange.fetch_ohlcv(symbol, timeframe='1h', since=current_price[0] - period, limit=1)[0][4]
    result = current_price[4] / (period_price * 0.01)
    return f"{(result - 100):.2f}"
