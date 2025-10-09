from django.urls import include, path
from . import views
from .views import CustomLoginView, CustomLogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', views.registro, name='register'),
    path('ar_condicionado/', include('ar_condicionado.urls')), 
]