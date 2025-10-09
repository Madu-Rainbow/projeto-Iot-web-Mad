from django.db import models

from django.db import models

class ArCondicionado(models.Model):
    ligado = models.BooleanField(default=False)
    temperatura = models.IntegerField(default=24)
    modo = models.CharField(max_length=20, default='Frio')
    velocidade = models.CharField(max_length=10, default='Média')

    def __str__(self):
        return f"ArCondicionado - {self.id}"
