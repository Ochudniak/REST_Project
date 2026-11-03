from django.urls import path

from .views import LoginView, UserCreateView, UserCreateViewById, RegisterView, SecureLoginView

urlpatterns = [
    path("users/", UserCreateView.as_view()),
    path("users/<int:user_id>/", UserCreateViewById.as_view()),
    path("users/login/", LoginView.as_view()),
    path("register/", RegisterView.as_view(), name="register"),
    path("auth/login/", SecureLoginView.as_view(), name="secure-login"),
]
