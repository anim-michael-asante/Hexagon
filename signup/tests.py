from django.contrib.auth.models import User
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .models import UserProfile


class SignupFlowTests(TestCase):
    def test_signup_rejects_malformed_input(self):
        response = self.client.post(reverse('signup:signup'), {
            'username': 'ada smith',
            'projector_id': 'HEXAGON 001',
            'phone_number': 'not-a-phone',
            'password1': 'A-secure-password-123',
            'password2': 'different-password-123',
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors['username'])
        self.assertTrue(form.errors['projector_id'])
        self.assertTrue(form.errors['phone_number'])
        self.assertTrue(form.errors['password2'])

    def test_signup_creates_profile_and_logs_user_in(self):
        response = self.client.post(reverse('signup:signup'), {
            'username': 'ada',
            'projector_id': 'HEXAGON-001',
            'phone_number': '+15551234567',
            'password1': 'A-secure-password-123',
            'password2': 'A-secure-password-123',
        })
        self.assertRedirects(response, reverse('signup:welcome'))
        self.assertTrue(self.client.session.get('_auth_user_id'))
        self.assertTrue(User.objects.filter(username='ada').exists())
        self.assertTrue(UserProfile.objects.filter(projector_id='HEXAGON-001', phone_number='+15551234567').exists())

    def test_signup_rejects_case_insensitive_duplicate_email(self):
        User.objects.create_user(username='existing', password='A-secure-password-123')
        response = self.client.post(reverse('signup:signup'), {
            'username': 'EXISTING',
            'projector_id': 'HEXAGON-002',
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

    def test_settings_updates_profile_and_user(self):
        user = User.objects.create_user(username='ada', password='A-secure-password-123')
        UserProfile.objects.create(
            user=user,
            projector_id='HEXAGON-003',
            phone_number='+15551234567',
        )
        self.client.force_login(user)
        response = self.client.post(reverse('signup:settings'), {
            'username': 'ada-new',
            'mfa_enabled': 'on',
            'phone_number': '+15557654321',
        })
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(user.username, 'ada-new')
        self.assertTrue(profile.mfa_enabled)
        self.assertEqual(profile.phone_number, '+15557654321')

    def test_settings_stores_uploaded_user_image(self):
        user = User.objects.create_user(username='image-user', password='A-secure-password-123')
        profile = UserProfile.objects.create(
            user=user,
            projector_id='HEXAGON-004',
            phone_number='+15551234567',
        )
        self.client.force_login(user)
        image = SimpleUploadedFile('avatar.png', b'\x89PNG\r\n\x1a\n', content_type='image/png')
        response = self.client.post(reverse('signup:settings'), {
            'username': 'image-user',
            'phone_number': '+15551234567',
            'user_image': image,
        })
        self.assertEqual(response.status_code, 200)
        profile.refresh_from_db()
        self.assertTrue(profile.user_image.name.startswith('profile-images/'))

    def test_profile_image_requires_authentication(self):
        response = self.client.get(reverse('signup:profile-image'))
        self.assertRedirects(response, f'{reverse("signup:login")}?next={reverse("signup:profile-image")}')

    def test_delete_account_removes_user_and_profile_image(self):
        user = User.objects.create_user(username='delete-user', password='A-secure-password-123')
        profile = UserProfile.objects.create(
            user=user,
            projector_id='HEXAGON-005',
            phone_number='+15551234567',
        )
        self.client.force_login(user)
        response = self.client.post(reverse('signup:delete-account'), {'confirmation': 'DELETE'})
        self.assertRedirects(response, reverse('signup:signup'))
        self.assertFalse(User.objects.filter(pk=user.pk).exists())
        self.assertFalse(UserProfile.objects.filter(pk=profile.pk).exists())

    def test_account_data_export_requires_login_and_returns_account_data(self):
        user = User.objects.create_user(username='export-user', password='A-secure-password-123')
        UserProfile.objects.create(
            user=user,
            projector_id='HEXAGON-006',
            phone_number='+15551234567',
        )
        self.client.force_login(user)
        response = self.client.get(reverse('signup:export-data'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], 'export-user')
