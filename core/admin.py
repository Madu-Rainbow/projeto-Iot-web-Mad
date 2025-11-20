from django.contrib import admin
from .models import Ambiente, Dispositivo, TipoSensor, Sensor, LeituraSensor

"""_summary_

    @admin.register(TipoSensor)
class TipoSensorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'unidade', 'descricao']
    search_fields = ['nome', 'unidade']
    ordering = ['nome']
        _type_: _description_
    """


@admin.register(Ambiente)
class AmbienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'usuario', 'total_dispositivos', 'total_sensores', 'criado_em']
    list_filter = ['usuario', 'criado_em']
    search_fields = ['nome', 'descricao']
    ordering = ['nome']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)

    def save_model(self, request, obj, form, change):
        if not change:  # Se for um novo objeto
            obj.usuario = request.user
        obj.save()


@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'ambiente', 'status', 'usuario', 'is_online', 'ultimo_contato']
    list_filter = ['tipo', 'status', 'ambiente', 'usuario', 'criado_em']
    search_fields = ['nome', 'modelo', 'fabricante', 'mac_address', 'ip_address']
    ordering = ['nome']
    
    fieldsets = [
        ('Informações Básicas', {
            'fields': ['nome', 'tipo', 'ambiente', 'status']
        }),
        ('Especificações Técnicas', {
            'fields': ['modelo', 'fabricante', 'mac_address', 'ip_address', 'firmware_versao']
        }),
        ('Descrição', {
            'fields': ['descricao'],
            'classes': ['collapse'],
        }),
        ('Conexão', {
            'fields': ['ultimo_contato'],
            'classes': ['collapse'],
        }),
    ]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)

    def save_model(self, request, obj, form, change):
        if not change:  # Se for um novo objeto
            obj.usuario = request.user
        obj.save()

    def is_online(self, obj):
        return obj.is_online
    is_online.boolean = True
    is_online.short_description = 'Online'


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'dispositivo', 'ambiente', 'ativo', 'total_leituras', 'ultima_leitura_valor']
    list_filter = ['tipo', 'ativo', 'ambiente', 'usuario', 'criado_em']
    search_fields = ['nome', 'dispositivo__nome', 'ambiente__nome']
    ordering = ['nome']
    
    fieldsets = [
        ('Informações Básicas', {
            'fields': ['nome', 'tipo', 'dispositivo', 'ambiente', 'ativo']
        }),
        ('Configurações', {
            'fields': ['valor_minimo', 'valor_maximo', 'precisao']
        }),
        ('Descrição', {
            'fields': ['descricao'],
            'classes': ['collapse'],
        }),
    ]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)

    def save_model(self, request, obj, form, change):
        if not change:  # Se for um novo objeto
            obj.usuario = request.user
        obj.save()

    def ultima_leitura_valor(self, obj):
        leitura = obj.ultima_leitura
        if leitura:
            return f"{leitura.valor} {obj.tipo.unidade}"
        return "Nenhuma leitura"
    ultima_leitura_valor.short_description = 'Última Leitura'


"""     
@admin.register(LeituraSensor)
class LeituraSensorAdmin(admin.ModelAdmin):
    list_display = ['sensor', 'valor_formatado', 'timestamp', 'observacao']
    list_filter = ['sensor__tipo', 'sensor__ambiente', 'timestamp']
    search_fields = ['sensor__nome', 'observacao']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(sensor__usuario=request.user)

    def has_add_permission(self, request):
        # Normalmente as leituras são adicionadas automaticamente
        return request.user.is_superuser

    def valor_formatado(self, obj):
        return obj.valor_formatado
    valor_formatado.short_description = 'Valor'
"""
# Personalizando o título do admin
admin.site.site_header = "Sistema IoT - Administração"
admin.site.site_title = "Sistema IoT"
admin.site.index_title = "Painel de Controle"
