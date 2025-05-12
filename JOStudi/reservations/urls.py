from django.urls import path
from . import views

urlpatterns = [
    path('mock_payment/', views.mock_payment, name='mock_payment'),
]