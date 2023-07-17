from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
import ccxt
from .tasks import test_func, get_price_change
from celery import shared_task
from .functions import CRYPTOGRAPHIC_KEY


class ApiContainer(models.Model):
    exchange = models.CharField(_("exhcange"), choices=((exchange, exchange) for exchange in ccxt.exchanges))
    name = models.CharField(_("name"), max_length=250)
    description = models.TextField(_("description"))
    apikey = models.CharField(_("apikey"), max_length=250)
    secret_key = models.BinaryField(_("secret key"), null=True, blank=True)
    user = models.ForeignKey(get_user_model(), verbose_name=_("user"), on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = _("Api container")
        verbose_name_plural = _("Api containers")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("apicontainer_detail", kwargs={"pk": self.pk})
    

class ExchangeModel(models.Model):
    exchange = models.CharField(_("exchange"), max_length=50)
    slug = models.SlugField(default="", null=False)
    

    def exchange_instance_with_api(self, apiKey=None, secret=None):
        if apiKey==None and secret==None:
            return self.exchange_instance
        elif apiKey and secret:
            return getattr(ccxt, self.exchange)(config={'apiKey': apiKey, 'secret': CRYPTOGRAPHIC_KEY.decrypt(bytes(secret))})
        
    @property
    def exchange_instance(self):
        return getattr(ccxt, self.exchange)()
    
    @property
    def exchange_markets(self):
        return self.exchange_instance.load_markets()
    
    def get_price_change(self, period, symbol):
        try:
            task_result = get_price_change.delay(period=period, exchange_name=self.exchange, symbol=symbol)
            price = task_result.get()
        except Exception as e:
            return f"get_price_change: {e}"
        return price
        # if price.find('-'):
        #     return mark_safe(f"<p style='color: green'>{price}</p>")
        # else:
        #     return mark_safe(f"<p style='color: red'>{price}</p>")
    
    @property
    def get_markets_with_period_prices(self):
        markets_with_periods = {}
        for market in self.exchange_markets.keys():
            market = market.replace("/", "")
            markets_with_periods[market] = {
                "1h": self.get_price_change(3600000, market), 
                "24h": self.get_price_change(86400000, market),
                "7d": self.get_price_change(604800000, market),
                "30d": self.get_price_change(2592000000, market),
                "365d": self.get_price_change(31536000000, market)
                }
        return markets_with_periods
    
    @property
    def get_info(self):
        return self.exchange_instance.describe
    
    @shared_task(bind=True)
    def fetch_ohlcv(self, get, symbol, timeframe='1m', since=None, limit=None, params={}):
        all_symbol_current_prices = {}

        #market = symbol.replace("/", "")
        try:
            result_instance = self.exchange_instance.fetch_ohlcv(symbol=symbol, timeframe=timeframe, since=since, limit=limit, params=params)[0]
        except Exception as e:
            return f"fetch_ohlcv: {e}"
        all_symbol_current_prices[symbol] = {
            'timestamp': result_instance[0],
            'open': result_instance[1],
            'high': result_instance[2],
            'low': result_instance[3],
            'close': result_instance[4],
            'volume': result_instance[5],
            }
        if get.lower() == 'all':
            return all_symbol_current_prices
        return all_symbol_current_prices[symbol][get]
        #return self.exchange_instance.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit, params=params)

    class Meta:
        verbose_name = _("Exchange model")
        verbose_name_plural = _("Exchange models")

    def __str__(self):
        return self.exchange

    def get_absolute_url(self):
        return reverse("ExchangeModel_detail", kwargs={"pk": self.pk})
