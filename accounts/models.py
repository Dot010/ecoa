from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField("e-mail", unique=True)
    name = models.CharField("nome", max_length=50, blank=True)
    bio = models.CharField("bio", max_length=160, blank=True)
    avatar = models.ImageField(
        "foto de perfil", upload_to="avatars/", blank=True, null=True
    )
    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True,
        verbose_name="seguindo",
    )

    def __str__(self):
        return f"@{self.username}"
