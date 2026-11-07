from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import UserProfile


class SignupFlowTests(TestCase):
    def test_signup_creates_profile_and_logs_user_in(self):
        response = self.client.post(reverse('signup:signup'), {
            'username': 'ada',
            'projector_id': 'ASP-001',
            'phone_number': '+15551234567',
            'password1': 'A-secure-password-123',
            'password2': 'A-secure-password-123',
        })
        self.assertRedirects(response, reverse('signup:welcome'))
        self.assertTrue(self.client.session.get('_auth_user_id'))
        self.assertTrue(User.objects.filter(username='ada').exists())
        self.assertTrue(UserProfile.objects.filter(projector_id='ASP-001', phone_number='+15551234567').exists())

    def test_signup_rejects_case_insensitive_duplicate_email(self):
        User.objects.create_user(username='existing', password='A-secure-password-123')
        response = self.client.post(reverse('signup:signup'), {
            'username': 'EXISTING',
            'projector_id': 'ASP-002',
            'phone_number': '+15551234567',
            'password1': 'A-secure-password-123',
            'password2': 'A-secure-password-123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'That username is already in use.')

    def test_login_accepts_case_insensitive_email(self):
        User.objects.create_user(username='ada', password='A-secure-password-123')
        response = self.client.post(reverse('signup:login'), {
            'username': 'ADA',
            'password': 'A-secure-password-123',
        })
        self.assertRedirects(response, reverse('signup:welcome'))

    def test_password_reset_request_is_generic_for_unknown_username(self):
        response = self.client.post(reverse('signup:forgot-password'), {
            'username': 'does-not-exist',
        })
        self.assertRedirects(response, reverse('signup:forgot-password-done'))
        self.assertContains(self.client.get(reverse('signup:forgot-password-done')), 'same for every request')
