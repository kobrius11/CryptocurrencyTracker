from typing import Any, Dict
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from django.forms.models import model_to_dict
from . import forms
from . import models
from .functions import sort_time, CRYPTOGRAPHIC_KEY
from .tasks import test_func, get_price_change
from crypto_tracker.celery import debug_task

from celery import current_app as app
from django_celery_beat.models import PeriodicTask
from celery.result import AsyncResult
#news stuff (news.html)
from GoogleNews import GoogleNews

# ccxt stuff (chart.html)
import ccxt
import pandas as pd



# Create your views here.
def index(request):
    # get latest news
    search_terms = ['Crypto', 'Stocks', 'Forex', 'Futures', 'Indices', 'Bonds']
    articles = []
    print(test_func.delay())
    debug_task.delay()
    for term in search_terms:
        news_class = GoogleNews()
        news_class.get_news(term)
        article = news_class.results(sort=False)[0] # neveikia sort funkcija, nes datetime.datetime < float, neiseina lygint
        articles.append(article)

    # get price data (last closed price)
    exchange = ccxt.binance()
    BTCUSDT = exchange.fetch_ohlcv('BTCUSDT', limit=2)[0][4] # BITCOIN / USDT
    ETHUSDT = exchange.fetch_ohlcv('ETHUSDT', limit=2)[0][4] # ETHERIUM / USDT
    BUSDUSDT = exchange.fetch_ohlcv('BUSDUSDT', limit=2)[0][4] # USDOLLAR / USDT
    BNBUSDT = exchange.fetch_ohlcv('BNBUSDT', limit=2)[0][4] # BINANCECOIN / USDT
    USDCUSDT = exchange.fetch_ohlcv('USDCUSDT', limit=2)[0][4] # USDCOIN / USDT

    BTCUSDT_24h_task = PeriodicTask.objects.filter(name="BTCUSDT")
    BTCUSDT_24h_result = BTCUSDT_24h_task.first().result if BTCUSDT_24h_task.first().ready() else None

    context = {
        'articles': articles,
        'room_name': 'track',
        'BTCUSDT': {'current': BTCUSDT, 
                    '1h': BTCUSDT_24h_result,}
        #             '24h': get_price_change.delay(period=86400000, symbol='BTCUSDT'),
        #             '7d': get_price_change.delay(period=604800000, symbol='BTCUSDT'),
        #             '30d': get_price_change.delay(period=2592000000, symbol='BTCUSDT'),
        #             '365d': get_price_change.delay(period=31536000000, symbol='BTCUSDT')
        #             },
        # 'ETHUSDT': {'current': ETHUSDT, 
        #             '1h': get_price_change.delay(period=3600000, symbol='ETHUSDT'), #period=3600000, symbol='ETHUSDT'
        #             '24h': get_price_change.delay(period=86400000, symbol='ETHUSDT'), #period=86400000, symbol='ETHUSDT'
        #             '7d': get_price_change.delay(period=604800000, symbol='ETHUSDT'), #period=604800000, symbol='ETHUSDT'
        #             '30d': get_price_change.delay(period=2592000000, symbol='ETHUSDT'), #period=2592000000, symbol='ETHUSDT'
        #             '365d': get_price_change.delay(period=31536000000, symbol='ETHUSDT') #period=31536000000, symbol='ETHUSDT'
        #             },
        # 'BUSDUSDT': {'current': BUSDUSDT, 
        #             '1h': get_price_change.delay(period=3600000, symbol='BUSDUSDT'),
        #             '24h': get_price_change.delay(period=86400000, symbol='BUSDUSDT'),
        #             '7d': get_price_change.delay(period=604800000, symbol='BUSDUSDT'),
        #             '30d': get_price_change.delay(period=2592000000, symbol='BUSDUSDT'),
        #             '365d': get_price_change.delay(period=31536000000, symbol='BUSDUSDT')
        #             },
        # 'BNBUSDT': {'current': BNBUSDT, 
        #             '1h': get_price_change.delay(period=3600000, symbol='BNBUSDT'),
        #             '24h': get_price_change.delay(period=86400000, symbol='BNBUSDT'),
        #             '7d': get_price_change.delay(period=604800000, symbol='BNBUSDT'),
        #             '30d': get_price_change.delay(period=2592000000, symbol='BNBUSDT'),
        #             '365d': get_price_change.delay(period=31536000000, symbol='BNBUSDT')},
        # 'USDCUSDT': {'current': USDCUSDT, 
        #             '1h': get_price_change.delay(period=3600000, symbol='USDCUSDT'),
        #             '24h': get_price_change.delay(period=86400000, symbol='USDCUSDT'),
        #             '7d': get_price_change.delay(period=604800000, symbol='USDCUSDT'),
        #             '30d': get_price_change.delay(period=2592000000, symbol='USDCUSDT'),
        #             '365d': get_price_change.delay(period=31536000000, symbol='USDCUSDT')},
    }

    return render(request, 'tracker_site/index.html', context)


def news(request):
    form = forms.NewsSearchBar()
    search = request.GET.get('search')
    sort_option = request.GET.get('sort')
    if search:
        news_class = GoogleNews()
        news_class.get_news(search)
        articles = news_class.results(sort=True) # '<' not supported between instances of 'float' and 'datetime.datetime'
        if sort_option == 'desc':
            articles = articles.sort(key=sort_time)
    else:
        articles = None
    
    context = {
        'articles': articles,
        'form': form,
    }
    return render(request, 'tracker_site/news.html', context=context)

class ExchangesListView(generic.ListView):
    model = models.ExchangeModel
    template_name = 'tracker_site/exchanges_list.html'
    
    def get_queryset(self):
        sort_option = self.request.GET.get('sort')
        qs = super().get_queryset()
        if sort_option == 'name':
            qs = qs.order_by('exchange')
        return qs
    

class ExchangeDetailView(APIView):
    model = models.ExchangeModel
    template_name = 'tracker_site/exchange_detail.html'

    
    def get_price_change_async(self, period, symbol):
        obj = get_object_or_404(models.ExchangeModel, slug=self.kwargs['slug'])
        try:
            task_result = get_price_change.delay(period=period, exchange_name='binance', symbol=symbol)
            price = task_result.get()
        except Exception as e:
            return str(e)
        return price
    
    def get(self, request, slug):
        obj = get_object_or_404(models.ExchangeModel, slug=slug)
        price = get_price_change.delay(period=86400000, exchange_name='binance', symbol='BTCUSDT')

        exchange_data = model_to_dict(obj)

        data = {
            'exchange': obj.exchange,
            'price': price,
        }
        return Response(data)
    

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
    success_url = reverse_lazy('dashboard_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api_obj = get_object_or_404(models.ApiContainer, id=self.kwargs['pk'])
        ccxt_obj = get_object_or_404(models.ExchangeModel, exchange=api_obj.exchange)

        context["api_obj"] = api_obj
        context["ccxt_obj"] = ccxt_obj.exchange_instance_with_api(
            apiKey=api_obj.apikey,
            secret=api_obj.secret_key
        )
        return context
    

class DashboardCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.ApiContainer
    form_class = forms.ApiContainerCreateForm 
    template_name = 'tracker_site/dashboard_create.html'
    success_url = reverse_lazy('dashboard_list')

    def form_valid(self, form):
        form = super().get_form(self.form_class)
        instance = form.save(commit=False)
        form.save(False)
        result = bytes(form.cleaned_data['secret_key_text'], encoding='utf-8')
        form.instance.secret_key = CRYPTOGRAPHIC_KEY.encrypt(result) 
        form.save(False)
        form.instance.user = self.request.user
        return super().form_valid(form)
    
class DashboardDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView
):
    model = models.ApiContainer
    template_name = 'tracker_site/dashboard_delete.html'
    success_url = reverse_lazy('dashboard_list')

    def form_valid(self, form):
        messages.success(self.request, _('Container is now deleted.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        api_obj = get_object_or_404(models.ApiContainer, id=self.kwargs['pk'])
        context['container'] = api_obj
        return context
    
    def test_func(self) -> bool | None:
        api_obj = get_object_or_404(models.ApiContainer, id=self.kwargs['pk'])
        return api_obj.user == self.request.user