from django.shortcuts import render
from offers.models import Offre
import json
from cart.cart import Cart

def home(request):
    offres = Offre.objects.all()
    return render(request, 'home.html', {'offres': offres})