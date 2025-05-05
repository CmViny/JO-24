from django.shortcuts import get_object_or_404, render
from offers.models import Offre

def offer(request, pk):
    offre = get_object_or_404(Offre, id=pk)
    return render(request, 'offre.html', {'offre': offre})