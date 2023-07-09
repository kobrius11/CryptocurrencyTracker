from django.urls import path
from . import views

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("sign-up/", views.signup, name="sign-up"),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
]