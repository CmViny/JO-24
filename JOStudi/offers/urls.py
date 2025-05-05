from django.urls import path
from . import views

urlpatterns = [
    path('offer/<uuid:pk>', views.offer, name='offer'),
]