from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    can_manage_subscribers = models.BooleanField(default=False)
    can_add_own_subscribers = models.BooleanField(default=True)

    def __str__(self):
        return self.username