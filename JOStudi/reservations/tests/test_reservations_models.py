from datetime import date
import pytest
import uuid
from django.utils import timezone
from reservations.models import Transaction, Reservation, QRCode
from accounts.models import Utilisateur
from offers.models import Offre
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# -------------------------
# Transaction code generation tests
# -------------------------
@pytest.mark.django_db
def test_generate_code_transaction_not_empty():
    transaction = Transaction(montant=15.50, statut=Transaction.REUSSIE)
    transaction.generate_code_transaction(transaction)
    transaction.save()
    assert transaction.code_transaction is not None
    assert len(transaction.code_transaction) > 0

@pytest.mark.django_db
def test_generate_code_transaction_is_unique():
    transaction1 = Transaction(montant=20.0, statut=Transaction.REUSSIE)
    transaction1.generate_code_transaction(transaction1)
    transaction1.save()

    transaction2 = Transaction(montant=30.0, statut=Transaction.EN_ATTENTE)
    transaction2.generate_code_transaction(transaction2)
    transaction2.save()

    assert transaction1.code_transaction != transaction2.code_transaction

@pytest.mark.django_db
def test_code_transaction_persists_on_save():
    transaction = Transaction.objects.create(
        montant=10.0,
        statut=Transaction.REUSSIE
    )
    original_code = transaction.code_transaction
    transaction.montant = 12.0
    transaction.save()
    assert transaction.code_transaction == original_code

@pytest.mark.django_db
def test_transaction_creation_fails_without_mandatory_fields():
    with pytest.raises(IntegrityError):
        Transaction.objects.create()

# -------------------------
# Reservation and Transaction coherence tests
# -------------------------
@pytest.mark.django_db
def test_reservation_transaction_coherence(django_user_model):
    user = django_user_model.objects.create_user(username="user_test", password="pass")
    utilisateur = user.utilisateur
    offre = Offre.objects.create(
        titre="Offre Test",
        description="desc",
        prix=10.0,
        type_billet=Offre.SOLO,
        date_disponible=timezone.now().date()
    )
    transaction = Transaction.objects.create(montant=10.0, statut=Transaction.REUSSIE)

    reservation = Reservation.objects.create(
        utilisateur=utilisateur,
        offre=offre,
        transaction=transaction,
        statut=Reservation.CONFIRMEE,
        type_billet='solo'
    )
    assert reservation.transaction == transaction

# -------------------------
# Reservation validation tests
# -------------------------
@pytest.mark.django_db
def test_reservation_invalid_statut_type_billet_raises_error(django_user_model):
    user = django_user_model.objects.create_user(username="user_test2", password="pass")
    utilisateur = user.utilisateur
    offre = Offre.objects.create(
        titre="Offre Test 2",
        description="desc",
        prix=10.0,
        type_billet=Offre.SOLO,
        date_disponible=timezone.now().date()
    )

    with pytest.raises(ValidationError):
        reservation = Reservation(
            utilisateur=utilisateur,
            offre=offre,
            statut='invalid_status',
            type_billet='solo'
        )
        reservation.full_clean()

    with pytest.raises(ValidationError):
        reservation = Reservation(
            utilisateur=utilisateur,
            offre=offre,
            statut=Reservation.EN_ATTENTE,
            type_billet='invalid_type'
        )
        reservation.full_clean()

@pytest.mark.django_db
def test_reservation_creation_without_utilisateur_or_offre_raises_error():
    with pytest.raises(IntegrityError):
        Reservation.objects.create(offre=None, utilisateur=None)

# -------------------------
# QRCode uniqueness and creation tests
# -------------------------
@pytest.mark.django_db
def test_qrcode_unique_per_reservation(django_user_model):
    user = django_user_model.objects.create_user(username="user_test3", password="pass")
    utilisateur = user.utilisateur
    offre = Offre.objects.create(
        titre="Offre Test 3",
        description="desc",
        prix=10.0,
        type_billet=Offre.SOLO,
        date_disponible=timezone.now().date()
    )
    reservation = Reservation.objects.create(utilisateur=utilisateur, offre=offre)
    qr1 = QRCode.objects.create(reservation=reservation, code="code_unique")
    
    with pytest.raises(IntegrityError):
        QRCode.objects.create(reservation=reservation, code="code_unique_2")

# -------------------------
# Additional Transaction tests
# -------------------------
@pytest.mark.django_db
def test_transaction_creation(django_user_model):
    transaction = Transaction.objects.create(montant=49.99)
    assert isinstance(transaction.id, uuid.UUID)
    assert transaction.statut == Transaction.EN_ATTENTE
    assert transaction.montant == 49.99
    assert transaction.date_transaction.date() == timezone.now().date()
    assert transaction.code_transaction is None
    assert str(transaction).startswith("Transaction")

@pytest.mark.django_db
def test_generate_code_transaction_saves_code():
    transaction = Transaction(montant=10.00)
    transaction.generate_code_transaction(transaction)
    transaction.save()
    assert transaction.code_transaction is not None
    assert len(transaction.code_transaction) == 32

# -------------------------
# Reservation creation tests
# -------------------------
@pytest.mark.django_db
def test_reservation_creation(django_user_model):
    user = django_user_model.objects.create_user(username="user1", password="pass")
    utilisateur = user.utilisateur
    offre = Offre.objects.create(titre="Offre 1",
        description="Test description",
        prix=10.00,
        type_billet=Offre.SOLO,
        date_disponible=date.today(),)
    reservation = Reservation.objects.create(utilisateur=utilisateur, offre=offre)
    assert isinstance(reservation.id, uuid.UUID)
    assert reservation.statut == Reservation.EN_ATTENTE
    assert reservation.type_billet == "solo"
    assert reservation.utilisateur == utilisateur
    assert str(reservation).startswith("Réservation")

# -------------------------
# QRCode creation and image tests
# -------------------------
@pytest.mark.django_db
def test_qrcode_creation_and_save(django_user_model):
    user = django_user_model.objects.create_user(username="user2", password="pass")
    utilisateur = user.utilisateur
    offre = Offre.objects.create(titre="Offre 2",
        description="Test description",
        prix=15.00,
        type_billet=Offre.SOLO,
        date_disponible=date.today(),)
    reservation = Reservation.objects.create(utilisateur=utilisateur, offre=offre)
    qr_code = QRCode(code="ABC123", reservation=reservation)
    qr_code.save()
    assert qr_code.image is not None
    assert qr_code.code == "ABC123"
    assert str(qr_code).startswith("QR")

@pytest.mark.django_db
def test_qrcode_image_not_regenerated_if_exists(django_user_model):
    user = django_user_model.objects.create_user(username="user3", password="pass")
    utilisateur = user.utilisateur
    offre = Offre.objects.create(titre="Offre 3",
        description="Test description",
        prix=20.00,
        type_billet=Offre.SOLO,
        date_disponible=date.today(),)
    reservation = Reservation.objects.create(utilisateur=utilisateur, offre=offre)
    qr_code = QRCode.objects.create(code="XYZ789", reservation=reservation)
    old_image = qr_code.image
    qr_code.save()

    assert qr_code.image == old_image