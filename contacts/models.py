from django.db import models
from django.contrib.auth.models import User


class Contact(models.Model):
    first_name = models.CharField(max_length=30, default='')
    last_name = models.CharField(max_length=30, default='')
    phone = models.CharField(max_length=20, default='')
    email = models.EmailField(default='')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    entry_date = models.DateTimeField(blank=True, null=True)
    birthday = models.DateTimeField(blank=True, null=True, default='')

    class Meta:
        verbose_name_plural = 'contacts'

    @property
    def full_name(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def __unicode__(self):
        return u'%s' % self.full_name

    def __str__(self):
        return u'%s %s' % (self.first_name, self.last_name)
