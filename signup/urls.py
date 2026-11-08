from django.urls import path

from .views import ASPLoginView, ASPLogoutView, delete_account, export_account_data, forgot_password, forgot_password_done, legal_page, profile_image, settings_page, signup, welcome

app_name = 'signup'

urlpatterns = [
    path('', signup, name='signup'),
    path('login/', ASPLoginView.as_view(), name='login'),
    path('forgot-password/', forgot_password, name='forgot-password'),
    path('forgot-password/done/', forgot_password_done, name='forgot-password-done'),
    path('legal/<slug:page>/', legal_page, name='legal'),
    path('logout/', ASPLogoutView.as_view(), name='logout'),
    path('welcome/', welcome, name='welcome'),
    path('settings/', settings_page, name='settings'),
    path('settings/delete-account/', delete_account, name='delete-account'),
    path('settings/export-data/', export_account_data, name='export-data'),
    path('profile-image/', profile_image, name='profile-image'),
]
