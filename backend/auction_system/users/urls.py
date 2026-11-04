from django.urls import path

from .views import RegisterView, SecureLoginView, CurrentUserView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("auth/login/", SecureLoginView.as_view(), name="secure-login"),
    path("auth/me/", CurrentUserView.as_view(), name="current-user"),
]
