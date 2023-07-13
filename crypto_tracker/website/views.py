from typing import Any
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.utils.translation import gettext_lazy as _
from . import forms
from . import models
from .functions import get_price_change, CRYPTOGRAPHIC_KEY

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

    context = {
        'articles': articles,
        'BTCUSDT': {'current': BTCUSDT, 
                    '1h': get_price_change(period=3600000),
                    '24h': get_price_change(period=86400000),
                    # '7d': get_price_change(period=604800000),
                    # '30d': get_price_change(period=2592000000),
                    # '365d': get_price_change(period=31536000000)
                    },
        'ETHUSDT': {'current': ETHUSDT, 
                    '1h': get_price_change(period=3600000, symbol='ETHUSDT'),
                    '24h': get_price_change(period=86400000, symbol='ETHUSDT'),
                    # '7d': get_price_change(period=604800000, symbol='ETHUSDT'),
                    # '30d': get_price_change(period=2592000000, symbol='ETHUSDT'),
                    # '365d': get_price_change(period=31536000000, symbol='ETHUSDT')
                    },
        'BUSDUSDT': {'current': BUSDUSDT, 
                    '1h': get_price_change(period=3600000, symbol='BUSDUSDT'),
                    '24h': get_price_change(period=86400000, symbol='BUSDUSDT'),
                    # '7d': get_price_change(period=604800000, symbol='BUSDUSDT'),
                    # '30d': get_price_change(period=2592000000, symbol='BUSDUSDT'),
                    # '365d': get_price_change(period=31536000000, symbol='BUSDUSDT')
                    },
        # 'BNBUSDT': {'current': BNBUSDT, 
        #             '1h': get_price_change(period=3600000, symbol='BNBUSDT'),
        #             '24h': get_price_change(period=86400000, symbol='BNBUSDT'),
        #             '7d': get_price_change(period=604800000, symbol='BNBUSDT'),
        #             '30d': get_price_change(period=2592000000, symbol='BNBUSDT'),
        #             '365d': get_price_change(period=31536000000, symbol='BNBUSDT')},
        # 'USDCUSDT': {'current': USDCUSDT, 
        #             '1h': get_price_change(period=3600000, symbol='USDCUSDT'),
        #             '24h': get_price_change(period=86400000, symbol='USDCUSDT'),
        #             '7d': get_price_change(period=604800000, symbol='USDCUSDT'),
        #             '30d': get_price_change(period=2592000000, symbol='USDCUSDT'),
        #             '365d': get_price_change(period=31536000000, symbol='USDCUSDT')},
    }

    return render(request, 'tracker_site/index.html', context)


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

class ExchangesListView(generic.ListView):
    model = models.ExchangeModel
    template_name = 'tracker_site/exchanges_list.html'
    
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.all()
        return qs
    

class ExchangeDetailView(generic.DeleteView):
    model = models.ExchangeModel
    template_name = 'tracker_site/exchange_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = get_object_or_404(models.ExchangeModel, slug=self.kwargs['slug'])
        
        context['exchange'] = obj
        context["markets"] = obj.exchange_markets.keys()
        # context["markets_with_periods"] = obj.get_markets_with_period_prices
        return context
    



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