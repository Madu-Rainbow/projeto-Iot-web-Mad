from django.shortcuts import render

from django.shortcuts import render, redirect
from .models import ArCondicionado
import random
import datetime
from django.utils import timezone


def painel(request):
    ar = ArCondicionado.objects.first()
    if not ar:
        ar = ArCondicionado.objects.create()

    # Início do contador
    if ar.ligado and not ar.inicio_ligado:
        ar.inicio_ligado = timezone.now()
        ar.save()
    elif not ar.ligado and ar.inicio_ligado:
        ar.inicio_ligado = None
        ar.save()

    tempo_ligado = None
    if ar.ligado and ar.inicio_ligado:
        tempo_ligado = timezone.now() - ar.inicio_ligado


   # Simular pequenas variações de temperatura
    if ar.ligado:
        ar.temperatura += random.choice([-1, 0, 1])
        ar.save()

    context = {
        'ar': ar,
        'tempo_ligado': tempo_ligado
    }
    return render(request, 'painel.html', context)


def alternar_status(request):
    ar = ArCondicionado.objects.first()
    ar.ligado = not ar.ligado
    ar.save()
    return redirect('painel')


def aumentar_temp(request):
    ar = ArCondicionado.objects.first()
    if ar.ligado:
        ar.temperatura += 1
        ar.save()
    return redirect('painel')


def diminuir_temp(request):
    ar = ArCondicionado.objects.first()
    if ar.ligado:
        ar.temperatura -= 1
        ar.save()
    return redirect('painel')

