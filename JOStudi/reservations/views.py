from io import BytesIO
from django.core.files import File
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Transaction, Reservation, QRCode
from offers.models import Offre
from accounts.models import Utilisateur
from cart.cart import Cart
import uuid
from django.shortcuts import get_object_or_404
from .models import QRCode
import qrcode # type: ignore

@login_required
def commandes(request):
    current_user = Utilisateur.objects.get(user=request.user)

    # Récupère toutes les transactions réussies de l'utilisateur
    transactions = Transaction.objects.filter(
        reservation__utilisateur=current_user,
        statut=Transaction.REUSSIE
    ).distinct().order_by('-date_transaction')

    return render(request, 'commandes.html', {
        'transactions': transactions
    })

@login_required
def recapitulatif(request):
    code = request.GET.get('code')
    current_user = Utilisateur.objects.get(user=request.user)

    transaction = Transaction.objects.filter(
        code_transaction=code,
        reservation__utilisateur=current_user,
        statut=Transaction.REUSSIE
    ).distinct().first()

    if not transaction:
        return render(request, 'recapitulatif.html', {'error': 'Aucune transaction trouvée.'})

    reservations = Reservation.objects.filter(
        transaction=transaction,
        utilisateur=current_user
    ).select_related('offre', 'qrcode')

    return render(request, 'recapitulatif.html', {
        'reservations': reservations,
        'transaction': transaction,
    })

# QR code
@login_required
def billet_numerique(request, code):
    qr = get_object_or_404(QRCode, code=code)
    reservation = qr.reservation
    utilisateur = reservation.utilisateur

    print(f"QR Code : {qr}, Reservation : {reservation}, Utilisateur : {utilisateur}")

    if request.user != utilisateur.user:
        return HttpResponseForbidden("Vous n'avez pas accès à ce billet.")

    offre = reservation.offre

    return render(request, 'billet_numerique.html', {
        'qr': qr,
        'reservation': reservation,
        'utilisateur': utilisateur,
        'offre': offre
    })

def generate_qr_code(data):
    img = qrcode.make(data)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


@login_required
def mock_payment(request):
    cart = Cart(request)
    current_user = Utilisateur.objects.get(user=request.user)

    # Créer une transaction simulée
    total_amount = cart.get_totals()
    transaction = Transaction.objects.create(
        montant=total_amount,
        statut=Transaction.REUSSIE
    )
    transaction.generate_code_transaction()

    # Récupérer le code utilisateur
    code_utilisateur = current_user.code_utilisateur

    # Créer une réservation et QRCode par Billet
    for item in cart.cart.values():
        try:
            offre_id = item.get('id')
            quantity = item.get('quantity', 1)
            type_billet = item.get('type_billet')
            offre = Offre.objects.get(id=offre_id)

            for _ in range(quantity):  # Créer N réservations
                reservation = Reservation.objects.create(
                utilisateur=current_user,
                offre=offre,
                statut=Reservation.CONFIRMEE,
                transaction=transaction,
                type_billet=type_billet
            )
                
                # Génération du code et de l'URL
                code = f"{code_utilisateur}_{transaction.code_transaction}_{uuid.uuid4().hex[:6]}"
                qr_url = request.build_absolute_uri(reverse('billet_numerique', args=[code]))

                # Appel de la fonction pour générer l'image du QR code
                buffer = generate_qr_code(qr_url)

                # Enregistrement de l'image dans /media/uploads/qrcodes
                filename = f"{code}.png"
                django_file = File(buffer)

                # Associer le fichier à l'objet QRCode
                qr = QRCode.objects.create(
                    reservation=reservation,
                    code=code,
                    image=django_file)

        except Offre.DoesNotExist:
            continue

    cart.clear()
    current_user.old_cart = None
    current_user.save()

    reservations = Reservation.objects.filter(transaction=transaction).select_related('offre', 'qrcode')
    return render(request, 'recapitulatif.html', {'reservations': reservations,'transaction': transaction})