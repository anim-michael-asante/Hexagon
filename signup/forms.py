from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import transaction

from .models import UserProfile


SAFE_IDENTIFIER = RegexValidator(
    regex=r'^[a-zA-Z0-9._-]+$',
    message='Use only letters, numbers, dots, underscores, and hyphens.',
)
PHONE_NUMBER = RegexValidator(
    regex=r'^\+?[0-9().\-\s]{7,30}$',
    message='Enter a valid phone number.',
)


class SettingsForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        validators=[SAFE_IDENTIFIER],
        widget=forms.TextInput(attrs={'autocomplete': 'username'}),
    )
    clear_user_image = forms.BooleanField(required=False)

    class Meta:
        model = UserProfile
        fields = (
            'mfa_enabled', 'phone_number', 'user_image',
        )
        widgets = {
            'mfa_enabled': forms.CheckboxInput(),
            'phone_number': forms.TextInput(attrs={'type': 'tel', 'autocomplete': 'tel'}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number'].strip()
        if len([character for character in phone_number if character.isdigit()]) < 7:
            raise forms.ValidationError('Enter a valid phone number.')
        return phone_number

    def clean_username(self):
        return self.cleaned_data['username'].strip().lower()

    def clean_user_image(self):
        image = self.cleaned_data.get('user_image')
        if self.cleaned_data.get('clear_user_image'):
            return None
        if not image:
            return image
        if image.size > 2 * 1024 * 1024:
            raise forms.ValidationError('Choose an image smaller than 2 MB.')
        extension = image.name.rsplit('.', 1)[-1].lower() if '.' in image.name else ''
        signatures = {
            'jpg': (b'\xff\xd8\xff',),
            'jpeg': (b'\xff\xd8\xff',),
            'png': (b'\x89PNG\r\n\x1a\n',),
            'gif': (b'GIF87a', b'GIF89a'),
            'webp': (b'RIFF',),
        }
        if extension not in signatures or not any(image.read(len(signature)) == signature for signature in signatures[extension]):
            raise forms.ValidationError('Use a valid JPG, PNG, GIF, or WEBP image.')
        image.seek(0)
        return image


class SignUpForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label='Username',
        strip=True,
        validators=[SAFE_IDENTIFIER],
        widget=forms.TextInput(
            attrs={'autocomplete': 'username', 'maxlength': 150, 'required': True}
        ),
    )
    projector_id = forms.CharField(
        max_length=100,
        label='Projector ID',
        strip=True,
        validators=[SAFE_IDENTIFIER],
        widget=forms.TextInput(
            attrs={'autocomplete': 'off', 'maxlength': 100, 'required': True}
        ),
    )
    phone_number = forms.CharField(
        max_length=30,
        label='Phone number',
        validators=[PHONE_NUMBER],
        widget=forms.TextInput(
            attrs={'type': 'tel', 'autocomplete': 'tel', 'maxlength': 30, 'required': True}
        ),
    )
    password1 = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'minlength': 8, 'required': True}
        ),
    )
    password2 = forms.CharField(
        label='Confirm password',
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'minlength': 8, 'required': True}
        ),
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
        if len([character for character in phone_number if character.isdigit()]) < 7:
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
    username = forms.CharField(
        max_length=150,
        label='Username',
        widget=forms.TextInput(attrs={'autocomplete': 'username', 'required': True}),
    )
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'current-password', 'required': True}
        ),
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip().lower()
        if not username:
            raise forms.ValidationError('Enter your username.')
        return username


class ForgotPasswordForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label='Username',
        widget=forms.TextInput(attrs={'autocomplete': 'username', 'required': True}),
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip().lower()
        if not username:
            raise forms.ValidationError('Enter your username.')
        return username
