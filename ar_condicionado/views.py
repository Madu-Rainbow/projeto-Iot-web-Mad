from django.shortcuts import render

from django.shortcuts import render, redirect
from .models import ArCondicionado
import random

def painel(request):
    ar = ArCondicionado.objects.first()
    if not ar:
        ar = ArCondicionado.objects.create()

    # Simular pequenas variações de temperatura
    if ar.ligado:
        ar.temperatura += random.choice([-1, 0, 1])
        ar.save()

    context = {'ar': ar}
    return render(request, 'painel.html', context)


def alternar_status(request):
    ar = ArCondicionado.objects.first()
    ar.ligado = not ar.ligado
    ar.save()
    return redirect('painel')


def aumentar_temp(request):
    ar = ArCondicionado.objects.first()
    ar.temperatura += 1
    ar.save()
    return redirect('painel')


def diminuir_temp(request):
    ar = ArCondicionado.objects.first()
    ar.temperatura -= 1
    ar.save()
    return redirect('painel')
