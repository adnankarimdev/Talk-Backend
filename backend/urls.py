from django.urls import path

from .views import (sign_up_user, log_in_user)

urlpatterns = [
    path("sign-up/", sign_up_user, name="sign_up_user"),
    path("login/", log_in_user, name="log_in_user"),
]