from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db import transaction

from .models import UserProfile


class SignUpForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    projector_id = forms.CharField(max_length=100, label='Projector ID')
    phone_number = forms.CharField(
        max_length=30,
        label='Phone number',
        widget=forms.TextInput(attrs={'type': 'tel', 'autocomplete': 'tel'}),
    )
    password1 = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label='Confirm password',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip().lower()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('That username is already in use.')
        return username

    def clean_projector_id(self):
        projector_id = self.cleaned_data['projector_id'].strip()
        if UserProfile.objects.filter(projector_id__iexact=projector_id).exists():
            raise forms.ValidationError('That projector ID is already registered.')
        return projector_id

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number'].strip()
        if not any(character.isdigit() for character in phone_number):
            raise forms.ValidationError('Enter a valid phone number.')
        return phone_number

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        password_validation.validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            self.add_error('password2', 'Passwords do not match.')
        return cleaned_data

    @transaction.atomic
    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
        )
        UserProfile.objects.create(
            user=user,
            projector_id=self.cleaned_data['projector_id'],
            phone_number=self.cleaned_data['phone_number'],
        )
        return user


class ASPAuthenticationForm(AuthenticationForm):
    def clean_username(self):
        return self.cleaned_data['username'].strip().lower()


class ForgotPasswordForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')

    def clean_username(self):
        return self.cleaned_data['username'].strip().lower()
