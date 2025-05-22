import pytest
from decimal import Decimal
from datetime import date
from offers.models import Offre
import uuid
import pytest
from django.core.exceptions import ValidationError

# -------------------------
# Test creation of an offer
# -------------------------
@pytest.mark.django_db
def test_create_offre():
    offre = Offre.objects.create(
        titre="Offre Test",
        description="Description de test",
        prix=Decimal("25.00"),
        type_billet=Offre.SOLO,
        date_disponible=date.today()
    )
    assert isinstance(offre.id, uuid.UUID)
    assert offre.titre == "Offre Test"
    assert offre.prix == Decimal("25.00")
    assert offre.type_billet == Offre.SOLO
    assert offre.date_disponible == date.today()
    assert str(offre) == "Offre Test"

# -------------------------
# Test get_prix() with various ticket types
# -------------------------
@pytest.mark.django_db
@pytest.mark.parametrize("type_billet, expected_multiplier", [
    (Offre.SOLO, Decimal('1')),
    (Offre.DUO, Decimal('1.5')),
    (Offre.FAMILLE, Decimal('2')),
    ('unknown', Decimal('1')),
])
def test_get_prix(type_billet, expected_multiplier):
    prix_base = Decimal('20.00')
    offre = Offre.objects.create(
        titre="Test Offre Prix",
        prix=prix_base,
        type_billet=Offre.SOLO,
        date_disponible=date.today()
    )
    prix_calcule = offre.get_prix(type_billet)
    assert prix_calcule == prix_base * expected_multiplier

# -------------------------
# Test __str__ method of offer
# -------------------------
@pytest.mark.django_db
def test_offre_str_method():
    offre = Offre.objects.create(
        titre="Test String",
        prix=Decimal("15.00"),
        type_billet=Offre.FAMILLE,
        date_disponible=date.today()
    )
    assert str(offre) == "Test String"

# -------------------------
# Test required fields validation
# -------------------------
@pytest.mark.django_db
def test_offre_requires_fields():
    offre = Offre(
        titre="",
        prix=None,
        type_billet=Offre.SOLO,
        date_disponible=None
    )
    with pytest.raises(ValidationError):
        offre.full_clean()