from django.shortcuts import render, redirect
from django.http import request
from django.urls import reverse_lazy
from django.views import generic
from . import forms

#news stuff
from GoogleNews import GoogleNews


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
    return render(request, 'tracker_site/chart.html')

