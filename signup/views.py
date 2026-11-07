from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import LoginView, LogoutView
from django.core.cache import cache
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import redirect, render

from .forms import ASPAuthenticationForm, ForgotPasswordForm, SignUpForm


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
    return render(request, 'signup/welcome.html')
