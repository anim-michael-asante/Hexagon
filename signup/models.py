from django.conf import settings
from django.db import models
from pathlib import PurePath
from uuid import uuid4


def profile_image_upload_path(instance, filename):
    extension = PurePath(filename).suffix.lower()
    return f'profile-images/{uuid4().hex}{extension}'


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    projector_id = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=30)
    mode = models.CharField(max_length=20, default='Light')
    accent = models.CharField(max_length=20, default='navy')
    background = models.CharField(max_length=20, default='panel')
    foreground = models.CharField(max_length=20, default='navy')
    mfa_enabled = models.BooleanField(default=False)
    user_image = models.FileField(upload_to=profile_image_upload_path, blank=True)

    def __str__(self):
        return f'{self.user.get_full_name()} profile'
