from typing import Any, Dict, Optional, Type
from django.forms.models import BaseModelForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, request, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.urls import reverse_lazy
from django.views import generic
from django import forms as f
from django.utils.translation import gettext_lazy as _
from . import forms
from . import models

from crypto_tracker.local_settings import KEY_INSTANCE
from cryptography.fernet import Fernet

#news stuff (news.html)
from GoogleNews import GoogleNews

# ccxt stuff (chart.html)
import ccxt
import pandas as pd

def get_price_change(period=604800000, exchange=ccxt.binance(), symbol='BTCUSDT'):
    # hour=3600000, day=86400000, week=604800000, month(30days)=2592000000, year=31536000000
    current_price = exchange.fetch_ohlcv(symbol, limit=2)[0]
    period_price = exchange.fetch_ohlcv(symbol, since=current_price[0] - period, limit=1)[0]
    result = current_price[4] / (period_price[4] / 100)
    return f"{(result - 100):.2f}"


CRYPTOGRAPHIC_KEY = Fernet(KEY_INSTANCE)

# Create your views here.
def index(request):
    # get latest news
    search_terms = ['Crypto', 'Stocks', 'Forex', 'Futures', 'Indices', 'Bonds']
    articles = []

    for term in search_terms:
        news_class = GoogleNews()
        news_class.get_news(term)
        article = news_class.results(sort=False)[0]
        articles.append(article)

    # get price data (last closed price)
    exchange = ccxt.binance()
    BTCUSDT = exchange.fetch_ohlcv('BTCUSDT', limit=2)[0] # BITCOIN / USDT
    ETHUSDT = exchange.fetch_ohlcv('ETHUSDT', limit=2)[0] # ETHERIUM / USDT
    BUSDUSDT = exchange.fetch_ohlcv('BUSDUSDT', limit=2)[0] # USDOLLAR / USDT
    BNBUSDT = exchange.fetch_ohlcv('BNBUSDT', limit=2)[0] # BINANCECOIN / USDT
    USDCUSDT = exchange.fetch_ohlcv('USDCUSDT', limit=2)[0] # USDCOIN / USDT

    context = {
        'articles': articles,
        'BTCUSDT': {'current': BTCUSDT[4], 
                    '1h': get_price_change(period=3600000),
                    '24h': get_price_change(period=86400000),
                    '7d': get_price_change(period=604800000),
                    '30d': get_price_change(period=2592000000),
                    '365d': get_price_change(period=31536000000)},
        'ETHUSDT': {'current': ETHUSDT[4], 
                    '1h': get_price_change(period=3600000, symbol='ETHUSDT'),
                    '24h': get_price_change(period=86400000, symbol='ETHUSDT'),
                    '7d': get_price_change(period=604800000, symbol='ETHUSDT'),
                    '30d': get_price_change(period=2592000000, symbol='ETHUSDT'),
                    '365d': get_price_change(period=31536000000, symbol='ETHUSDT')},
        'BUSDUSDT': {'current': BUSDUSDT[4], 
                    '1h': get_price_change(period=3600000, symbol='BUSDUSDT'),
                    '24h': get_price_change(period=86400000, symbol='BUSDUSDT'),
                    '7d': get_price_change(period=604800000, symbol='BUSDUSDT'),
                    '30d': get_price_change(period=2592000000, symbol='BUSDUSDT'),
                    '365d': get_price_change(period=31536000000, symbol='BUSDUSDT')},
        'BNBUSDT': {'current': BNBUSDT[4], 
                    '1h': get_price_change(period=3600000, symbol='BNBUSDT'),
                    '24h': get_price_change(period=86400000, symbol='BNBUSDT'),
                    '7d': get_price_change(period=604800000, symbol='BNBUSDT'),
                    '30d': get_price_change(period=2592000000, symbol='BNBUSDT'),
                    '365d': get_price_change(period=31536000000, symbol='BNBUSDT')},
        'USDCUSDT': {'current': USDCUSDT[4], 
                    '1h': get_price_change(period=3600000, symbol='USDCUSDT'),
                    '24h': get_price_change(period=86400000, symbol='USDCUSDT'),
                    '7d': get_price_change(period=604800000, symbol='USDCUSDT'),
                    '30d': get_price_change(period=2592000000, symbol='USDCUSDT'),
                    '365d': get_price_change(period=31536000000, symbol='USDCUSDT')},
    }

    return render(request, 'tracker_site/index.html', context)

def get_currencies(request):
    selected_exchange = request.GET.get('exchange')

    if selected_exchange:
        try:
            exchange_instance = getattr(ccxt, selected_exchange)()
            exchange_instance.load_markets()
            currencies = {
                'currencies': exchange_instance.symbols
            }
            print(exchange_instance.symbols)
            return JsonResponse(currencies)
        except AttributeError:
            pass

    return JsonResponse({'currencies': []})

def news(request):
    form = forms.NewsSearchBar()
    search = request.GET.get('search')
    if search:
        news_class = GoogleNews()
        news_class.get_news(search)
        articles = news_class.results(sort=True)
    else:
        articles = None
    
    context = {
        'articles': articles,
        'form': form,
    }
    return render(request, 'tracker_site/news.html', context=context)


class Chart(generic.TemplateView):
    model = models.ExchangeModel
    # form_class = forms.ChartForm()
    template_name = 'tracker_site/chart.html'
    success_url = reverse_lazy('chart')

    def get_context_data(self, **kwargs: Any):
        context =  super().get_context_data(**kwargs)
        try:
            obj = get_object_or_404(models.ExchangeModel, exchange=self.request.GET.get('exchange'))
        except:
            obj = get_object_or_404(models.ExchangeModel, exchange='ace')

        
        context = {
            "exchanges": self.model.objects.all(),
            "exchange": self.request.GET.get('exchange'),
            "tradingview_button": "False",
            'markets_list': obj.exchange_markets
            
        }
        return context
    
    
# Dashboard.html views
class DashboardListView(LoginRequiredMixin, generic.ListView):
    model = models.ApiContainer
    template_name = 'tracker_site/dashboard.html'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs
    

class DashboardDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.ApiContainer
    template_name = 'tracker_site/dashboard_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = get_object_or_404(models.ApiContainer, id=self.kwargs['pk'])
        print(bytes(obj.secret_key))
        print(obj.secret_key)
        print(obj.secret_key)
        context["api_obj"] = obj
        context["ccxt_obj"] = getattr(ccxt, obj.exchange)(config={
            'apiKey': obj.apikey,
            'secret': CRYPTOGRAPHIC_KEY.decrypt(bytes(obj.secret_key)),
        })
        return context
    

class DashboardCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.ApiContainer
    form_class = forms.ApiContainerCreateForm 
    #f.modelform_factory(model, form=f.ModelForm, fields={
    #     'exchange': f.ChoiceField(label=_('exchange'), choices=ccxt.exchanges),
    #     'name': f.ChoiceField(label=_('exchange'), choices=ccxt.exchanges), 
    #     'apikey': f.CharField(label=_('API')), 
    #     'secret_key': f.PasswordInput()
    #     })
    template_name = 'tracker_site/dashboard_create.html'
    success_url = reverse_lazy('dashboard_list')

    def form_valid(self, form):
        form = super().get_form(self.form_class)
        form.instance.user = self.request.user
        form.save(False)
        result = bytes(form.cleaned_data['secret_key_text'], encoding='utf-8')
        form.instance.secret_key = CRYPTOGRAPHIC_KEY.encrypt(result) 
        # form.instance.secret_key = make_password(form.cleaned_data['secret_key'], salt=local_settings.HASHING_SALT)[33:]
        form.save(False)
        return super().form_valid(form)