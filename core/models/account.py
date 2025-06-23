from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


# User model
class User(AbstractUser):
    USER_TYPE = (
        ('student', _('Student')),
        ('teacher', _('Teacher')),
    )
    avatar = models.ImageField(_('Avatar'), upload_to='core/account/users/', blank=True, null=True)
    user_type = models.CharField(_('User type'), max_length=32, choices=USER_TYPE, default='student')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
