from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import ccxt
from .functions import get_price_change


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

    @property
    def exchange_instance(self):
        return getattr(ccxt, self.exchange)()
    
    @property
    def exchange_markets(self):
        return self.exchange_instance.load_markets()
    
    def get_price_change(self, period, symbol):
        return get_price_change(period=period, exchange=self.exchange_instance, symbol=symbol)
    
    @property
    def get_markets_with_period_prices(self):
        markets_with_periods = {}
        for market in self.exchange_markets.keys():
            market = market.replace("/", "")
            markets_with_periods[market] = {
                "1h": self.get_price_change(3600000, market), 
                # "24h": self.get_price_change(86400000, market),
                # "7d": self.get_price_change(604800000, market),
                # "30d": self.get_price_change(2592000000, market),
                # "365d": self.get_price_change(31536000000, market)
                }
        return markets_with_periods

    
    class Meta:
        verbose_name = _("Exchange model")
        verbose_name_plural = _("Exchange models")

    def __str__(self):
        return self.exchange

    def get_absolute_url(self):
        return reverse("ExchangeModel_detail", kwargs={"pk": self.pk})
