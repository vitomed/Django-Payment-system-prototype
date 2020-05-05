from django.urls import path
from django.contrib.auth import views as auth_views

from account.views import account, Register, TransferView

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', Register.as_view(), name='register'),
    path('transfer/', TransferView.as_view(), name='transfer'),
    path('', account, name='account'),
]