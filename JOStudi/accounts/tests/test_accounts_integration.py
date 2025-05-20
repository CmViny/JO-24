from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class AccountsIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_registration_login_profile_flow(self):
        # 1. Register
        self.client.post(reverse('register'), {
            'username': 'flowuser',
            'first_name': 'Flow',
            'last_name': 'User',
            'email': 'flow@user.com',
            'password1': 'FlowPass123!',
            'password2': 'FlowPass123!',
        })
        self.assertTrue(User.objects.filter(username='flowuser').exists())

        # 2. Login
        login_success = self.client.login(username='flowuser', password='FlowPass123!')
        self.assertTrue(login_success)

        # 3. Access to a protected page
        response = self.client.get(reverse('update_profile'))
        self.assertEqual(response.status_code, 200)

    def test_access_protected_view_without_login(self):
        response = self.client.get(reverse('update_profile'))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertIn('/login', response.url)