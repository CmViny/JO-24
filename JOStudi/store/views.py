from django.shortcuts import render
from offers.models import Offre

def home(request):
    offres = Offre.objects.all()
    return render(request, 'home.html', {'offres': offres})