from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.painel, name='painel'),
    path('alternar/', views.alternar_status, name='alternar'),
    path('aumentar/', views.aumentar_temp, name='aumentar'),
    path('diminuir/', views.diminuir_temp, name='diminuir'),
]