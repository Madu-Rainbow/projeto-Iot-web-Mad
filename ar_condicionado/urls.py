from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.painel, name='painel'),
    path('<int:pk>/', views.painel, name='painel_pk'),

    
    
    path('alternar/', views.alternar_status, name='alternar'),
    path('<int:pk>/alternar/', views.alternar_status, name='alternar_with_pk'),

    path('ar_condicionado/<int:pk>/aumentar/', views.aumentar, name='aumentar_with_pk'),
    path('ar_condicionado/<int:pk>/diminuir/', views.diminuir, name='diminuir_with_pk'),

    path('alterar_modo/', views.alterar_modo, name='alterar_modo'),
    path('<int:pk>/alterar_modo/', views.alterar_modo, name='alterar_modo_with_pk'),
]