from django.shortcuts import render

from django.shortcuts import render, redirect,get_object_or_404
from .models import ArCondicionado
import random
import datetime
from django.utils import timezone

def _get_ar(pk=None):
    """Retorna o ArCondicionado pelo pk se fornecido, senão o primeiro (cria se não existir)."""
    if pk:
        return get_object_or_404(ArCondicionado, pk=pk)
    ar = ArCondicionado.objects.first()
    if not ar:
        ar = ArCondicionado.objects.create()
    return ar

def painel(request, pk=None):
    ar = None
    tempo_ligado = None

    if pk is None:
        first = ArCondicionado.objects.first()
        if first:
            # Redireciona para a URL correta com o PK do primeiro objeto
            return redirect('painel_pk', pk=first.pk) 
        
        # Se não há PK e NÃO há objetos cadastrados, 'ar' permanece None.
        # Renderizamos o template com context={'ar': None, 'tempo_ligado': None}
    
    else:
        # Cenário 2: PK fornecido (Execução normal)
        ar = _get_ar(pk)
        
        # Lógica de Tempo e Variação (Mantida)
        tempo_ligado_seconds = 0
    if ar.ligado and ar.inicio_ligado:
        # Pega a diferença de tempo (timedelta)
        tempo_delta = timezone.now() - ar.inicio_ligado
        # Converte para segundos (inteiro)
        tempo_ligado_seconds = int(tempo_delta.total_seconds())
        
       # if ar.ligado:
        #    ar.temperatura += random.choice([-1, 0, 1])
         #   ar.save()

    # Passamos sempre 'ar' e 'tempo_ligado', que podem ser None.
    context = {
        'ar': ar,
        'tempo_ligado_seconds': tempo_ligado_seconds
    }
    return render(request, 'painel.html', context)

def alternar_status(request, pk=None):
    ar = _get_ar(pk)
    if not ar:
        return redirect('painel')
    ar.ligado = not ar.ligado
    ar.save()
    return redirect('painel_pk', pk=ar.pk)

def aumentar(request, pk):
    ar = _get_ar(pk) # Função para buscar o objeto por PK
    if request.method == 'POST' and ar.ligado:
        if ar.temperatura < 30:
            ar.temperatura += 1
        ar.save()
    return redirect('painel_pk', pk=pk)

def diminuir(request, pk):
    ar = _get_ar(pk)
    if request.method == 'POST' and ar.ligado:
        if ar.temperatura > 18:
            ar.temperatura -= 1
        ar.save()
    return redirect('painel_pk', pk=pk)

def alterar_modo(request, pk=None):
    ar = _get_ar(pk)
    if request.method == 'POST':
        modo = request.POST.get('modo')
        if modo is not None:
            # opcional: normalizar capitalização conforme seu modelo
            ar.modo = modo
            ar.save()
    # sempre redireciona para o painel do aparelho (com pk)
    return redirect('painel_pk', pk=ar.pk)