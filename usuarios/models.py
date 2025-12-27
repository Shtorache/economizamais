
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_TYPES = (('CONSUMIDOR','Consumidor'),('PARCEIRO','Parceiro'))
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tipo = models.CharField(max_length=20, choices=USER_TYPES, default='CONSUMIDOR')
    cidade = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.tipo}'
