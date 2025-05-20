import pytest
from django.urls import reverse
from offers.models import Offre
from datetime import date
import uuid

# -------------------------
# Fixture for creating a sample offer
# -------------------------
@pytest.fixture
def offre(db):
    return Offre.objects.create(
        titre="Test Offre",
        description="Test description",
        prix=10.00,
        type_billet=Offre.SOLO,
        date_disponible=date.today(),
    )

# -------------------------
# Test cart summary view
# -------------------------
@pytest.mark.django_db
def test_cart_summary_view(client):
    response = client.get(reverse("cart_summary"))
    assert response.status_code == 200
    assert "cart_total" in response.context
    assert "cart_offres" in response.context

# -------------------------
# Test adding an offer to the cart
# -------------------------
@pytest.mark.django_db
def test_cart_add_view(client, offre):
    response = client.post(reverse("cart_add"), {
        "action": "post",
        "offre_id": str(offre.id),
        "quantity": 2,
        "type_billet": "duo"
    })
    assert response.status_code == 200
    data = response.json()
    assert "qty" in data
    assert "cart_total" in data
    assert float(data["cart_total"]) == 10.0 * 1.5 * 2

# -------------------------
# Test updating an item in the cart
# -------------------------
@pytest.mark.django_db
def test_cart_update_view(client, offre):
    client.post(reverse("cart_add"), {
        "action": "post",
        "offre_id": str(offre.id),
        "quantity": 1,
        "type_billet": "solo"
    })

    key = f"{offre.id}_solo"
    response = client.post(reverse("cart_update"), {
        "action": "post",
        "key": key,
        "quantity": 3,
        "type_billet": "famille"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Cart updated"
    assert float(data["updated_price"]) == 10.0 * 2
    assert float(data["total_price"]) == 10.0 * 2 * 3
    assert "cart_total" in data

# -------------------------
# Test deleting an item from the cart
# -------------------------
@pytest.mark.django_db
def test_cart_delete_view(client, offre):
    client.post(reverse("cart_add"), {
        "action": "post",
        "offre_id": str(offre.id),
        "quantity": 1,
        "type_billet": "solo"
    })

    key = f"{offre.id}_solo"
    response = client.post(reverse("cart_delete"), {
        "action": "delete",
        "offre_id": key,
    })

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Item deleted"
    assert data["cart_quantity"] == 0
    assert data["cart_total"] == "0.00"

# -------------------------
# Test adding an invalid offer to the cart
# -------------------------
@pytest.mark.django_db
def test_cart_add_invalid_offer(client):
    invalid_uuid = uuid.uuid4()
    response = client.post(reverse("cart_add"), {
        "action": "post",
        "offre_id": str(invalid_uuid),
        "quantity": 1,
        "type_billet": "solo"
    })
    assert response.status_code == 404

# -------------------------
# Test updating cart with invalid key
# -------------------------
@pytest.mark.django_db
def test_cart_update_invalid_key(client):
    key = "00000000-0000-0000-0000-000000000000_solo"
    response = client.post(reverse("cart_update"), {
        "action": "post",
        "key": key,
        "quantity": 1,
        "type_billet": "solo"
    })
    assert response.status_code in (400, 404)