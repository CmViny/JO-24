import datetime
import pytest
from django.urls import reverse
from offers.models import Offre
from decimal import Decimal
from datetime import date
import uuid
from django.core.files.uploadedfile import SimpleUploadedFile

# -------------------------
# Test offer view with a valid UUID
# -------------------------
@pytest.mark.django_db
def test_offer_view_valid_uuid(client):
    image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
    offre = Offre.objects.create(
        titre="Offre Test",
        prix=Decimal("20.00"),
        date_disponible=datetime.date.today(),
        type_billet='solo',
        image=image,
    )
    response = client.get(reverse("offer", args=[offre.id]))
    assert response.status_code == 200
    assert "offre" in response.context
    assert response.context["offre"].id == offre.id

# -------------------------
# Test offer view with an invalid UUID
# -------------------------
@pytest.mark.django_db
def test_offer_view_invalid_uuid(client):
    invalid_uuid = uuid.uuid4()
    url = reverse('offer', kwargs={'pk': invalid_uuid})
    response = client.get(url)
    assert response.status_code == 404

# -------------------------
# Test formules view returns offers and formules
# -------------------------
@pytest.mark.django_db
def test_formules_view(client):
    image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")

    Offre.objects.create(
        titre="Offre Test",
        prix=Decimal("20.00"),
        date_disponible=datetime.date.today(),
        type_billet='solo',
        image=image
    )
    response = client.get(reverse("formules"))
    assert response.status_code == 200
    assert "offres" in response.context
    assert "formules" in response.context