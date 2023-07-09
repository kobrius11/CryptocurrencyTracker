from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('news/', views.news, name='news'),
    path('chart/', views.Chart.as_view(), name='chart'),
    path('dashboard/', views.DashboardListView.as_view(), name='dashboard_list'),
    path('dashboard/create', views.DashboardCreateView.as_view(), name='dashboard_create'),
    path('dashboard/<int:pk>', views.DashboardDetailView.as_view(), name='dashboard_detail'),
]