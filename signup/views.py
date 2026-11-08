from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import LoginView, LogoutView
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.http import FileResponse, Http404, JsonResponse
from pathlib import PurePath
from django.shortcuts import redirect, render

from .forms import ASPAuthenticationForm, ForgotPasswordForm, SettingsForm, SignUpForm
from .models import UserProfile


THROTTLE_WINDOW = 15 * 60
MAX_ATTEMPTS = 5


def _client_key(request, purpose):
    address = request.META.get('REMOTE_ADDR', 'unknown')
    return f'auth-throttle:{purpose}:{address}'


def _is_throttled(request, purpose):
    return (cache.get(_client_key(request, purpose)) or 0) >= MAX_ATTEMPTS


def _record_failure(request, purpose):
    key = _client_key(request, purpose)
    cache.add(key, 0, THROTTLE_WINDOW)
    cache.incr(key)


def _reset_request_key(request):
    return f'auth-throttle:password-reset:{request.META.get("REMOTE_ADDR", "unknown")}'


def signup(request):
    if request.user.is_authenticated:
        return redirect('signup:welcome')

    form = SignUpForm(request.POST or None)
    if request.method == 'POST':
        if _is_throttled(request, 'signup'):
            form.add_error(None, 'Too many attempts. Please try again in 15 minutes.')
        elif form.is_valid():
            try:
                user = form.save()
            except IntegrityError:
                form.add_error('username', 'That username is already in use.')
            else:
                login(request, user)
                return redirect('signup:welcome')
        else:
            _record_failure(request, 'signup')
    return render(request, 'signup/signup.html', {'form': form})


class ASPLoginView(LoginView):
    template_name = 'signup/login.html'
    authentication_form = ASPAuthenticationForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        if _is_throttled(self.request, 'login'):
            form.add_error(None, 'Too many attempts. Please try again in 15 minutes.')
        else:
            _record_failure(self.request, 'login')
            form.add_error(None, 'Username or password is incorrect.')
        return super().form_invalid(form)


class ASPLogoutView(LogoutView):
    next_page = 'signup:login'


def forgot_password(request):
    form = ForgotPasswordForm(request.POST or None)
    if request.method == 'POST':
        key = _reset_request_key(request)
        if (cache.get(key) or 0) >= MAX_ATTEMPTS:
            form.add_error(None, 'Too many requests. Please try again in 15 minutes.')
        elif form.is_valid():
            cache.add(key, 0, THROTTLE_WINDOW)
            cache.incr(key)
            username = form.cleaned_data['username']
            user = User.objects.filter(username__iexact=username, is_active=True).first()
            if user and user.email:
                PasswordResetForm({'email': user.email}).save(
                    request=request,
                    use_https=request.is_secure(),
                    from_email=None,
                    email_template_name='registration/password_reset_email.html',
                    subject_template_name='registration/password_reset_subject.txt',
                )
            return redirect('signup:forgot-password-done')
    return render(request, 'signup/forgot_password.html', {'form': form})


def forgot_password_done(request):
    return render(request, 'signup/forgot_password_done.html')


def legal_page(request, page):
    legal_pages = {
        'terms': ('Terms and Conditions', 'Our Terms and Conditions are being prepared and will be published before launch.'),
        'privacy': ('Privacy Policy', 'Our Privacy Policy is being prepared and will be published before launch.'),
        'cookies': ('Cookie Policy', 'Our Cookie Policy is being prepared and will be published before launch.'),
        'acceptable-use': ('Acceptable Use', 'Our Acceptable Use Policy is being prepared and will be published before launch.'),
    }
    try:
        title, message = legal_pages[page]
    except KeyError as exc:
        raise Http404 from exc
    return render(request, 'signup/legal.html', {'legal_title': title, 'legal_message': message})


@login_required
def welcome(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    return render(request, 'signup/welcome.html', {'user_profile': profile})


@login_required
def settings_page(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return redirect('signup:welcome')
    form = SettingsForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exclude(pk=request.user.pk).exists():
            form.add_error(None, 'That username is already in use or invalid.')
        else:
            request.user.username = username
            request.user.save(update_fields=['username'])
            if form.cleaned_data.get('clear_user_image') and profile.user_image:
                profile.user_image.delete(save=False)
                profile.user_image = ''
            else:
                profile = form.save()
            profile.save()
            return render(request, 'signup/settings.html', {'form': form, 'saved': True, 'user_profile': profile})
    return render(request, 'signup/settings.html', {'form': form, 'user_profile': profile})


@login_required
def profile_image(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    if not profile or not profile.user_image:
        raise Http404
    content_types = {
        '.gif': 'image/gif',
        '.jpeg': 'image/jpeg',
        '.jpg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
    }
    content_type = content_types.get(PurePath(profile.user_image.name).suffix.lower(), 'application/octet-stream')
    response = FileResponse(profile.user_image.open('rb'), content_type=content_type)
    response['X-Content-Type-Options'] = 'nosniff'
    response['Content-Disposition'] = 'inline'
    return response


@login_required
@transaction.atomic
def delete_account(request):
    if request.method != 'POST' or request.POST.get('confirmation') != 'DELETE':
        return redirect('signup:settings')
    profile = UserProfile.objects.filter(user=request.user).first()
    if profile and profile.user_image:
        profile.user_image.delete(save=False)
    user = request.user
    logout(request)
    user.delete()
    return redirect('signup:signup')


@login_required
def export_account_data(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    data = {
        'username': request.user.username,
        'phone_number': profile.phone_number if profile else '',
        'settings': {
            'mfa_enabled': profile.mfa_enabled if profile else False,
        },
    }
    response = JsonResponse(data)
    response['Content-Disposition'] = 'attachment; filename="hexagon-account-data.json"'
    return response
from django.contrib.auth import logout
from django.db import transaction
from django.http import FileResponse, Http404
from pathlib import PurePath
