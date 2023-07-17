from django.urls import path
from . import views

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("sign-up/", views.signup, name="sign-up"),
]