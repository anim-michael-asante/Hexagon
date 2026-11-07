from django.urls import path

from .views import ASPLoginView, ASPLogoutView, forgot_password, forgot_password_done, legal_page, signup, welcome

app_name = 'signup'

urlpatterns = [
    path('', signup, name='signup'),
    path('login/', ASPLoginView.as_view(), name='login'),
    path('forgot-password/', forgot_password, name='forgot-password'),
    path('forgot-password/done/', forgot_password_done, name='forgot-password-done'),
    path('legal/<slug:page>/', legal_page, name='legal'),
    path('logout/', ASPLogoutView.as_view(), name='logout'),
    path('welcome/', welcome, name='welcome'),
]
