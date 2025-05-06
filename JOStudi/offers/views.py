from django.shortcuts import get_object_or_404, render
from offers.models import Offre

def offer(request, pk):
    offre = get_object_or_404(Offre, id=pk)
    return render(request, 'offre.html', {'offre': offre})

def formules(request):
    offres = Offre.objects.all()

    formules = [
    {
        'label': 'Solo',
        'emoji': '🧍‍♂️',
        'description': 'Idéale pour une personne, cette formule vous permet d\'accéder à toutes les épreuves à un tarif standard.<br><br>Simple et efficace, elle convient parfaitement aux aventuriers en solo.',
    },
    {
        'label': 'Duo',
        'emoji': '👫',
        'description': 'Conçue pour deux participants, la formule Duo offre une expérience partagée à un tarif avantageux : seulement 1,5 fois le prix d’une formule Solo.<br><br>Une solution économique pour les couples ou amis.',
    },
    {
        'label': 'Famille',
        'emoji': '👨‍👩‍👧‍👦',
        'description': 'Parfaite pour les familles ou les groupes jusqu’à 4 personnes.<br><br>Avec un tarif deux fois supérieur à la formule Solo, vous bénéficiez d’un accès groupé pour vivre l’expérience ensemble à prix réduit par personne.',
    },
]


    return render(request, 'formules.html', {
        'offres': offres,
        'formules': formules,
    })
