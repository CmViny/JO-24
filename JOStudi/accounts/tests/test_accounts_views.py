from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Utilisateur
import pyotp  # type: ignore
import pytest

# -------------------------
# Tests for login with invalid credentials
# -------------------------
@pytest.mark.django_db
def test_login_post_wrong_credentials(client):
    session = client.session
    session['cart'] = {}
    session.save()

    response = client.post(reverse('login'), {
        'username': 'wronguser',
        'password': 'wrongpass'
    })

    assert response.status_code == 302
    assert response.url == reverse('login')

# -------------------------
# Tests for 2FA verification with invalid code
# -------------------------
@pytest.mark.django_db
def test_verify_2fa_post_invalid_code(client, django_user_model):
    user = django_user_model.objects.create_user(
        username='testuser',
        password='testpassword',
        email='test@example.com'
    )
    client.login(username='testuser', password='testpassword')

    session = client.session
    session['temp_totp_secret'] = pyotp.random_base32()
    session.save()

    response = client.post(reverse('verify_2fa'), {'code': '000000'}, follow=True)

    assert "Code incorrect." in response.content.decode()

# -------------------------
# Tests for account-related views
# -------------------------
@pytest.mark.django_db
class AccountsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='john', password='password123', email='john@example.com')
        self.utilisateur = self.user.utilisateur

    # -------------------------
    # Login & Logout views
    # -------------------------
    def test_login_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_post_success(self):
        User.objects.create_user(username="testuser", password="testpass123")
        session = self.client.session
        session["cart"] = {}
        session.save()

        response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "testpass123"
        })

        assert response.status_code == 302

    def test_logout(self):
        self.client.login(username='john', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('home'))

    # -------------------------
    # Registration view tests
    # -------------------------
    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_view(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@user.com',
            'password1': 'StrongPassword123',
            'password2': 'StrongPassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_password_mismatch(self):
        url = reverse('register')
        response = self.client.post(url, {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'password123',
            'password2': 'differentpassword',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Erreur lors de la création de votre compte")

    # -------------------------
    # 2FA verification with valid code
    # -------------------------
    def test_verify_2fa_post_valid_code(self):
        self.utilisateur.totp_secret = pyotp.random_base32()
        self.utilisateur.is_2fa_enabled = True
        self.utilisateur.save()
        self.client.login(username='john', password='password123')
        session = self.client.session
        session['temp_totp_secret'] = self.utilisateur.totp_secret
        session.save()

        totp = pyotp.TOTP(self.utilisateur.totp_secret)
        response = self.client.post(reverse('verify_2fa'), {'code': totp.now()})
        self.assertRedirects(response, reverse('home'))

    # -------------------------
    # Profile update views
    # -------------------------
    def test_update_profile_authenticated(self):
        self.client.login(username='john', password='password123')
        response = self.client.get(reverse('update_profile'))
        self.assertEqual(response.status_code, 200)

    def test_update_profile_unauthenticated(self):
        response = self.client.get(reverse('update_profile'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('update_profile')}")