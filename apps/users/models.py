from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    MEMBER = 'MEMBER'
    MANAGER = 'MANAGER'
    ADMIN = 'ADMIN'
    ROLES = [
        (MEMBER, 'Member'),
        (MANAGER, 'Manager'),
        (ADMIN, 'Admin'),
    ]
    role = models.CharField(max_length=9, choices=ROLES, default=MEMBER,)

    def __str__(self):
        return self.username
