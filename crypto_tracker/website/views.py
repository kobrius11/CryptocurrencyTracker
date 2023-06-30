from django.shortcuts import render, redirect
from django.http import request

#news stuff
from GoogleNews import GoogleNews


# Create your views here.
def index(request):
    return render(request, 'tracker_site/index.html')

def news(request):
    news_class = GoogleNews()
    news_class.get_news('Cryptocurrency')
    articles = news_class.results()

    context = {
        'articles': articles 
    }
    return render(request, 'tracker_site/news.html', context=context)

def chart(request):
    return render(request, 'tracker_site/chart.html')