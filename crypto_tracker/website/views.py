from typing import Any, Dict, Optional, Type
from django.forms.models import BaseModelForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, request
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


CRYPTOGRAPHIC_KEY = Fernet(KEY_INSTANCE)

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


class Chart(generic.FormView):
    form_class = forms.ChartForm()
    template_name = 'tracker_site/chart.html'
    success_url = reverse_lazy('chart')

    def get_form(self, form=form_class):
        #form = super().get_form(self.form_class)
        exchange_string = self.request.GET.get('exchange')
        print(exchange_string)
        if exchange_string:
            exchange_instance = getattr(ccxt, exchange_string)()
            exchange_instance.load_markets()
            form.fields['currencies'] = f.ChoiceField(label=_('currency'), choices=((symbol, symbol) for symbol in exchange_instance.symbols))
        return form

    def get_context_data(self, **kwargs: Any):
        context =  super().get_context_data(**kwargs)
        context = {
            "exchange": self.request.GET.get('exchange'),
            "currencies": self.request.GET.get('currencies'),
            "trading_view": self.request.GET.get('tradingview_button'),
            "form": self.form_class
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