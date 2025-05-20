import pytest
from django.test import RequestFactory
from offers.models import Offre
from cart.cart import Cart
import datetime
from decimal import Decimal
from django.contrib.auth.models import AnonymousUser

# -------------------------
# Fake session class for simulating Django sessions
# -------------------------
class FakeSession(dict):
    def __init__(self):
        super().__init__()
        self.modified = False

# -------------------------
# Fixtures
# -------------------------
@pytest.fixture
def fake_offre(db):
    return Offre.objects.create(
        titre="Offre Test",
        prix=Decimal("20.00"),
        date_disponible=datetime.date.today()
    )

@pytest.fixture
def request_factory():
    return RequestFactory()

@pytest.fixture
def empty_cart(request_factory):
    request = request_factory.get("/")
    request.session = FakeSession()
    request.user = AnonymousUser()
    return Cart(request)

# -------------------------
# Test adding to cart
# -------------------------
def test_add_to_cart(empty_cart, fake_offre):
    empty_cart.add(product=fake_offre, quantity=2, type_billet='famille')
    key = f"{fake_offre.id}_famille"
    assert len(empty_cart) == 1
    assert empty_cart.cart[key]['quantity'] == 2
    assert Decimal(empty_cart.cart[key]['price']) == Decimal('40.00')

# -------------------------
# Test total calculation
# -------------------------
def test_get_totals(empty_cart, fake_offre):
    empty_cart.add(product=fake_offre, quantity=1, type_billet='duo')
    total = empty_cart.get_totals()
    assert total == Decimal('30.00')

# -------------------------
# Test deleting from cart
# -------------------------
def test_delete_from_cart(empty_cart, fake_offre):
    empty_cart.add(product=fake_offre, quantity=1, type_billet='solo')
    empty_cart.delete(product=fake_offre)
    assert len(empty_cart) == 0

# -------------------------
# Test updating cart
# -------------------------
def test_update_cart(empty_cart, fake_offre):
    empty_cart.add(product=fake_offre, quantity=1, type_billet='solo')
    empty_cart.update(product=fake_offre, quantity=3, type_billet='duo')
    key = f"{fake_offre.id}_duo"
    assert key in empty_cart.cart
    assert empty_cart.cart[key]['quantity'] == 3
    assert Decimal(empty_cart.cart[key]['price']) == Decimal('30.00')

# -------------------------
# Test negative quantity handling
# -------------------------
def test_add_negative_quantity(empty_cart, fake_offre):
    with pytest.raises(ValueError):
        empty_cart.add(product=fake_offre, quantity=-1, type_billet='solo')

def test_update_negative_quantity(empty_cart, fake_offre):
    empty_cart.add(product=fake_offre, quantity=1, type_billet='solo')
    with pytest.raises(ValueError):
        empty_cart.update(product=fake_offre, quantity=-5, type_billet='solo')

# -------------------------
# Test clearing the cart
# -------------------------
def test_clear_cart(empty_cart):
    empty_cart.session['cart'] = {
        "some_key": {
            "id": "1",
            "title": "Test",
            "price": "10.00",
            "quantity": 1,
            "type_billet": "solo"
        }
    }
    empty_cart.clear()
    assert len(empty_cart.cart) == 0

# -------------------------
# Test total with ticket types
# -------------------------
def test_cart_total_calculation_with_types(empty_cart, fake_offre):
    empty_cart.add(product=fake_offre, quantity=2, type_billet='duo')
    total = empty_cart.get_totals()
    assert total == Decimal('60.00')

# -------------------------
# Test session modified flag
# -------------------------
def test_session_modified_flag(empty_cart, fake_offre):
    assert empty_cart.request.session.modified is False
    empty_cart.add(product=fake_offre, quantity=1, type_billet='solo')
    assert empty_cart.request.session.modified is True