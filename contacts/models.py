from django.db import models
from django.contrib.auth.models import User
from enum import Enum


class CivilStatus(Enum):
    SOLTERO = "Soltero"
    CASADO = "Casado"
    DIVORCIADO = "Divorciado"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Contact(models.Model):
    first_name = models.CharField(
        max_length=30,
        default='',
        blank=False,
        null=False
    )
    last_name = models.CharField(
        max_length=30,
        default='',
        blank=False,
        null=False
    )
    phone = models.IntegerField(
        max_length=30,
        default='',
        blank=False,
        null=False
    )
    email = models.EmailField(default='')
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    entry_date = models.DateTimeField(blank=True, null=True)
    birthday = models.DateTimeField(blank=True, null=True, default='')
    direction = models.CharField(
        max_length=30,
        default='',
        blank=False,
        null=False
    )
    province = models.CharField(
        max_length=30,
        default='',
        blank=False,
        null=False
    )
    civil_status = models.CharField(
        choices=CivilStatus.choices(),
        default=CivilStatus.SOLTERO,
        max_length=100)

    @property
    def full_name(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def __unicode__(self):
        return u'%s' % self.full_name

    def __str__(self):
        return u'%s %s' % (self.first_name, self.last_name)
