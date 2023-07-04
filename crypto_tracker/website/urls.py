from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('news/', views.news, name='news'),
    path('chart/', views.Chart.as_view(), name='chart')
]