from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    is_active = None

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['full_name', 'phone']

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE"
        NOT_ACTIVE = "BLOCKED"

    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        unique=True,
        error_messages={'unique': "A user is already registered with this email address"},
    )
    phone = models.CharField("номер телефона", max_length=32)
    full_name = models.CharField("полное имя", max_length=128)
    status = models.CharField("статус", choices=Status.choices, default=Status.ACTIVE)
