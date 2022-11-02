from django.db import models
from django.contrib.auth.models import AbstractUser

from attendance.models import School


class User(AbstractUser):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    TEACHER = "TEACHER"
    DRIVER = "DRIVER"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (MANAGER, "Manager"),
        (TEACHER, "Teacher"),
        (DRIVER, "Driver"),
    ]
    role = models.CharField(max_length=7, choices=ROLE_CHOICES, blank=True, null=True)
    school = models.ForeignKey(School, models.SET_NULL, blank=True, null=True)
