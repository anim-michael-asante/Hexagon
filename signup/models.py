from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    projector_id = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.user.get_full_name()} profile'
