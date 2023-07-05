from typing import Any, Dict
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, request
from django.urls import reverse_lazy
from django.views import generic
from django import forms as f
from django.utils.translation import gettext_lazy as _
from . import forms

#news stuff (news.html)
from GoogleNews import GoogleNews

# ccxt stuff (chart.html)
import ccxt
import pandas as pd

# Create your views here.
def index(request):
    return render(request, 'tracker_site/index.html')


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


def chart(request):
    form = forms.ChartForm()
    
    # trading view open/close button
    trading_view = request.GET.get('tradingview_button')


    exchange = request.GET.get('exchange')
    exchange_currencies = request.GET.get('currencies')
    exchange_instance = getattr(ccxt, exchange)()
    exchange_instance.load_markets()


    
    context = {
        "exchange": exchange,
        "currencies": exchange_currencies,
        "trading_view": trading_view,
        "form": form
    }
    
    print(exchange_instance)
    return render(request, 'tracker_site/chart.html', context)

class Chart(generic.FormView):
    form_class = forms.ChartForm()
    template_name = 'tracker_site/chart.html'
    success_url = reverse_lazy('chart')

    def form_valid(self, form=form_class):
        data = {
            "exchange": self.request.GET.get('exchange'),
            "currencies": self.request.GET.get('currencies'),
            # "trading_view": self.request.GET.get('tradingview_button'),
        }
        # Perform any necessary actions with the saved exchange, currencies, and trading_view values
        return data


    def get_form(self, form=form_class):
        # form = super().get_form(form)
        exchange_string = self.request.GET.get('exchange')
        if exchange_string:
            exchange_instance = getattr(ccxt, exchange_string)()
            exchange_instance.load_markets()
            form.fields['currencies'] = f.ChoiceField(label=_('currency'), choices=((symbol, symbol) for symbol in exchange_instance.symbols))
        return form

    def get_context_data(self, **kwargs: Any):
        context =  super().get_context_data(**kwargs)
        if self.form_valid():
            context = {
                "exchange": self.form_valid()['exchange'],
                "currencies": self.form_valid()['currencies'],
                "trading_view": self.request.GET.get('tradingview_button'),
                "form": self.form_class
            }
            return context
        context = {
            "exchange": self.request.GET.get('exchange'),
            "currencies": self.request.GET.get('currencies'),
            "trading_view": self.request.GET.get('tradingview_button'),
            "form": self.form_class
        }
        return context
    

    
