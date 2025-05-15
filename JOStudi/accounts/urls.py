from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('register', views.register_user, name='register'),
    path('update_profile', views.update_profile, name='update_profile'),
    path('activate-2fa/', views.activate_2fa, name='activate_2fa'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
]