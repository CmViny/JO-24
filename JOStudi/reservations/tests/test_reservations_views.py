from unittest.mock import patch
import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponseForbidden
from reservations.models import Transaction, Reservation, QRCode
from accounts.models import Utilisateur
from offers.models import Offre
from cart.cart import Cart
from django.utils import timezone

# -------------------------
# Orders view tests
# -------------------------
@pytest.mark.django_db
def test_commandes_view_authenticated(client, django_user_model):
    user = django_user_model.objects.create_user(username='user1', password='pass')
    utilisateur = user.utilisateur

    transaction = Transaction.objects.create(montant=20, statut=Transaction.REUSSIE)
    reservation = Reservation.objects.create(utilisateur=utilisateur, offre=Offre.objects.create(
        titre='Offre Test',
        description='desc',
        prix=10,
        type_billet='solo',
        date_disponible='2025-01-01'
    ), transaction=transaction, statut=Reservation.CONFIRMEE)

    client.login(username='user1', password='pass')
    url = reverse('commandes')
    response = client.get(url)

    assert response.status_code == 200
    assert transaction in response.context['transactions']

@pytest.mark.django_db
def test_commandes_view_unauthenticated(client):
    url = reverse('commandes')
    response = client.get(url)

    assert response.status_code == 302
    assert reverse('login') in response.url

# -------------------------
# Summary view tests with valid and invalid transaction codes
# -------------------------
@pytest.mark.django_db
def test_recapitulatif_view_with_valid_transaction(client, django_user_model):
    user = django_user_model.objects.create_user(username='user2', password='pass')
    utilisateur = user.utilisateur
    offre = Offre.objects.create(
        titre='Offre 2',
        description='desc',
        prix=15,
        type_billet='solo',
        date_disponible='2025-01-01'
    )
    transaction = Transaction.objects.create(montant=15, statut=Transaction.REUSSIE, code_transaction='code123')
    reservation = Reservation.objects.create(utilisateur=utilisateur, offre=offre, transaction=transaction)

    client.login(username='user2', password='pass')
    url = reverse('recapitulatif') + f'?code={transaction.code_transaction}'
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['transaction'] == transaction
    assert reservation in response.context['reservations']

@pytest.mark.django_db
def test_recapitulatif_view_with_invalid_transaction(client, django_user_model):
    user = django_user_model.objects.create_user(username='user3', password='pass')
    client.login(username='user3', password='pass')
    url = reverse('recapitulatif') + '?code=invalidcode'
    response = client.get(url)
    assert response.status_code == 200
    assert 'error' in response.context
    assert response.context['error'] == 'Aucune transaction trouvée.'

# -------------------------
# Digital ticket view access tests
# -------------------------
@pytest.mark.django_db
def test_billet_numerique_view_access_granted(client, django_user_model):
    user = django_user_model.objects.create_user(username='user4', password='pass')
    utilisateur = user.utilisateur
    offre = Offre.objects.create(
        titre='Offre 4',
        description='desc',
        prix=10,
        type_billet='solo',
        date_disponible='2025-01-01'
    )
    reservation = Reservation.objects.create(utilisateur=utilisateur, offre=offre)
    qr_code = QRCode.objects.create(reservation=reservation, code='qr123')

    client.login(username='user4', password='pass')
    url = reverse('billet_numerique', args=[qr_code.code])
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['qr'] == qr_code
    assert response.context['reservation'] == reservation
    assert response.context['utilisateur'] == utilisateur
    assert response.context['offre'] == offre

@pytest.mark.django_db
def test_billet_numerique_view_access_denied(client, django_user_model):
    user1 = django_user_model.objects.create_user(username='user5', password='pass')
    user2 = django_user_model.objects.create_user(username='user6', password='pass')
    utilisateur1 = user1.utilisateur
    utilisateur2 = user2.utilisateur
    offre = Offre.objects.create(
        titre='Offre 5',
        description='desc',
        prix=10,
        type_billet='solo',
        date_disponible='2025-01-01'
    )
    reservation = Reservation.objects.create(utilisateur=utilisateur1, offre=offre)
    qr_code = QRCode.objects.create(reservation=reservation, code='qr456')

    client.login(username='user6', password='pass')
    url = reverse('billet_numerique', args=[qr_code.code])
    response = client.get(url)

    assert response.status_code == 403

# -------------------------
# Mock payment flow tests
# -------------------------
@pytest.mark.django_db
def test_mock_payment_creates_transaction_and_reservations(client, django_user_model, mocker):
    # User creation
    user = django_user_model.objects.create_user(username="user7", password="pass")
    utilisateur = user.utilisateur

    # Offer creation
    from offers.models import Offre
    offre = Offre.objects.create(
        titre="Offre test",
        description="Description test",
        prix=30.00,
        type_billet=Offre.SOLO,
        date_disponible=timezone.now().date()
    )

    client.login(username="user7", password="pass")

    # Mock cart
    mock_cart = mocker.Mock()
    mock_cart.get_totals.return_value = 60  # cart total
    mock_cart.cart = {
        '1': {'id': offre.id, 'quantity': 2, 'type_billet': 'solo'}
    }
    mock_cart.clear = mocker.Mock()
    mocker.patch('reservations.views.Cart', return_value=mock_cart)

    # Patch build_absolute_uri
    with patch('django.http.HttpRequest.build_absolute_uri', return_value='http://testserver/fake_qr_code_url'):
        url = reverse('mock_payment')
        response = client.get(url)

    assert response.status_code == 200
    # Check that a transaction was created
    from reservations.models import Transaction, Reservation, QRCode
    transaction = Transaction.objects.first()
    assert transaction is not None
    assert transaction.statut == Transaction.REUSSIE
    assert transaction.montant == 60

    # Check that 2 reservations were created (quantity=2)
    reservations = Reservation.objects.filter(transaction=transaction)
    assert reservations.count() == 2

    # Check each reservation has an associated QRCode
    for reservation in reservations:
        qr = QRCode.objects.filter(reservation=reservation).first()
        assert qr is not None
        assert qr.code.startswith(utilisateur.code_utilisateur)

    # Check that the cart was cleared
    mock_cart.clear.assert_called_once()