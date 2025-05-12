from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Transaction, Reservation, QRCode
from offers.models import Offre
from accounts.models import Utilisateur
from cart.cart import Cart
import uuid

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
                
                # Générer un code QR unique
                code = f"{code_utilisateur}_{transaction.code_transaction}_{uuid.uuid4().hex[:6]}"

                QRCode.objects.create(
                    reservation=reservation,
                    code=code
                )
        except Offre.DoesNotExist:
            continue

    cart.clear()

    reservations = Reservation.objects.filter(transaction=transaction).select_related('offre', 'qrcode')
    return render(request, 'payment_success.html', {'reservations': reservations,'transaction': transaction})