from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

from django.urls import reverse



class Ambiente(models.Model):
    """Model para representar ambientes (ex: Sala, Cozinha, Jardim)"""
    nome = models.CharField(max_length=100, verbose_name='Nome')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Ambiente'
        verbose_name_plural = 'Ambientes'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse('ambiente_detail', kwargs={'pk': self.pk})

    @property
    def total_dispositivos(self):
        return self.dispositivos.count()

    @property
    def total_sensores(self):
        return self.sensores.count()


class Dispositivo(models.Model):
    """Model para representar dispositivos IoT"""
    TIPOS_DISPOSITIVO = [
        ('sensor', 'Sensor'),
        ('atuador', 'Atuador'),
        ('controlador', 'Controlador'),
        ('gateway', 'Gateway'),
        ('outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('manutencao', 'Manutenção'),
        ('erro', 'Erro'),
    ]

    nome = models.CharField(max_length=100, verbose_name='Nome')
    tipo = models.CharField(max_length=20, choices=TIPOS_DISPOSITIVO, verbose_name='Tipo')
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name='Modelo')
    fabricante = models.CharField(max_length=100, blank=True, null=True, verbose_name='Fabricante')
    mac_address = models.CharField(max_length=17, unique=True, verbose_name='Endereço MAC')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='Endereço IP')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo', verbose_name='Status')
    
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE, related_name='dispositivos', verbose_name='Ambiente')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    firmware_versao = models.CharField(max_length=50, blank=True, null=True, verbose_name='Versão do Firmware')
    
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    ultimo_contato = models.DateTimeField(blank=True, null=True, verbose_name='Último Contato')

    class Meta:
        verbose_name = 'Dispositivo'
        verbose_name_plural = 'Dispositivos'
        ordering = ['nome']

    def __str__(self):
        return getattr(self, 'nome', f'Dispositivo {self.pk}')

    def get_absolute_url(self):
        return reverse('dispositivo_detail', kwargs={'pk': self.pk})

    @property
    def is_online(self):
        """Verifica se o dispositivo está online baseado no último contato"""
        if not self.ultimo_contato:
            return False
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() - self.ultimo_contato < timedelta(minutes=5)

    @property
    def status_badge_class(self):
        """Retorna a classe CSS para o badge de status"""
        classes = {
            'ativo': 'bg-success',
            'inativo': 'bg-secondary',
            'manutencao': 'bg-warning',
            'erro': 'bg-danger',
        }
        return classes.get(self.status, 'bg-secondary')

        

    """
    class TipoSensor(models.Model):
    Model para tipos de sensores
    nome = models.CharField(max_length=50, unique=True, verbose_name='Nome')
    unidade = models.CharField(max_length=10, verbose_name='Unidade de Medida')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    
    class Meta:
        verbose_name = 'Tipo de Sensor'
        verbose_name_plural = 'Tipos de Sensores'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.unidade})"
"""
class TipoSensor(models.TextChoices):
    AR_CONDICIONADO = 'AC', 'Ar-Condicionado'
    LUZ = 'LUZ', 'Luz'
    




class Sensor(models.Model):
    """Model para representar sensores específicos"""
    nome = models.CharField(max_length=100, verbose_name='Nome')
    #tipo = models.ForeignKey(TipoSensor, on_delete=models.CASCADE, verbose_name='Tipo de Sensor')
    tipo = models.CharField(
        max_length=3, # Tamanho máximo da chave (AC, LUZ)
        choices=TipoSensor.choices,
        default=TipoSensor.LUZ,
        verbose_name='Tipo de Sensor'
    )
    
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='sensores', verbose_name='Dispositivo')
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE, related_name='sensores', verbose_name='Ambiente')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    
    valor_minimo = models.FloatField(blank=True, null=True, verbose_name='Valor Mínimo')
    valor_maximo = models.FloatField(blank=True, null=True, verbose_name='Valor Máximo')
    precisao = models.IntegerField(default=2, verbose_name='Precisão (casas decimais)')
    
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensores'
        ordering = ['nome']
        unique_together = ['dispositivo', 'tipo']

    def __str__(self):
        return f"{self.nome} - {self.get_tipo_display()}"

    def get_absolute_url(self):
        return reverse('sensor_detail', kwargs={'pk': self.pk})

    @property
    def ultima_leitura(self):
        """Retorna a última leitura do sensor"""
        return self.leituras.first()

    @property
    def total_leituras(self):
        """Retorna o total de leituras do sensor"""
        return self.leituras.count()


class LeituraSensor(models.Model):
    """Model para armazenar leituras dos sensores"""
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='leituras', verbose_name='Sensor')
    valor = models.FloatField(verbose_name='Valor')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')
    observacao = models.CharField(max_length=200, blank=True, null=True, verbose_name='Observação')

    class Meta:
        verbose_name = 'Leitura do Sensor'
        verbose_name_plural = 'Leituras dos Sensores'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sensor', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"{self.sensor.nome}: {self.valor} {self.sensor.tipo.unidade} ({self.timestamp})"

    @property
    def valor_formatado(self):
        """Retorna o valor formatado com a precisão definida"""
        precisao = self.sensor.precisao
        return f"{self.valor:.{precisao}f} {self.sensor.tipo.unidade}"
