from django.test import TestCase
from django.contrib.auth.models import User
from accounts.forms import SignUpForm, UpdateProfileForm

# -------------------------
# Tests for SignUpForm
# -------------------------
class SignUpFormTest(TestCase):
    def test_signup_form_valid(self):
        form_data = {
            'username': 'formuser',
            'first_name': 'Form',
            'last_name': 'User',
            'email': 'form@user.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_signup_form_password_mismatch(self):
        form_data = {
            'username': 'formuser',
            'password1': 'abc123',
            'password2': 'def456'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_signup_form_missing_fields(self):
        form = SignUpForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password1', form.errors)

    def test_signup_form_invalid_email(self):
        form_data = {
            'username': 'bademailuser',
            'email': 'not-an-email',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_signup_form_duplicate_username(self):
        User.objects.create_user(username='existinguser', password='test123')
        form_data = {
            'username': 'existinguser',
            'email': 'test@user.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

# -------------------------
# Tests for UpdateProfileForm
# -------------------------
class UpdateProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='updateuser', email='u@u.com')
        self.utilisateur = self.user.utilisateur

    def test_update_profile_initial_values(self):
        form = UpdateProfileForm(instance=self.user, utilisateur_instance=self.utilisateur)
        self.assertEqual(form.initial['email'], 'u@u.com')

    def test_update_profile_save(self):
        form_data = {
            'username': 'updateuser',
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'new@u.com',
            'age': 30,
            'telephone': '0123456789',
            'adresse': '123 rue Exemple'
        }
        form = UpdateProfileForm(data=form_data, instance=self.user, utilisateur_instance=self.utilisateur)
        self.assertTrue(form.is_valid())
        form.save(utilisateur_instance=self.utilisateur)
        self.utilisateur.refresh_from_db()
        self.assertEqual(self.utilisateur.telephone, '0123456789')

    def test_update_profile_invalid_email(self):
        form_data = {
            'username': 'updateuser',
            'email': 'bademail',
            'telephone': '0123456789'
        }
        form = UpdateProfileForm(data=form_data, instance=self.user, utilisateur_instance=self.utilisateur)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_update_profile_blank_fields(self):
        form_data = {
            'username': '',
            'email': '',
            'telephone': ''
        }
        form = UpdateProfileForm(data=form_data, instance=self.user, utilisateur_instance=self.utilisateur)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)

    def test_update_profile_user_not_changed(db):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )

        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
        }

        form = UpdateProfileForm(data=form_data, instance=user)
        assert form.is_valid()