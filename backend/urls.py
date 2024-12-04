from django.urls import path

from .views import (sign_up_user, 
                    log_in_user,
                    save_form_data)

urlpatterns = [
    path("sign-up/", sign_up_user, name="sign_up_user"),
    path("login/", log_in_user, name="log_in_user"),
    path("save-form-data/", save_form_data, name="save_form_data"),
]