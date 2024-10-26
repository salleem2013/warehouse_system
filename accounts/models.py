from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from devices.models import Facility


class CustomUser(AbstractUser):
    facility = models.OneToOneField(
        Facility, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Facility")
    )

    def __str__(self):
        return self.email
