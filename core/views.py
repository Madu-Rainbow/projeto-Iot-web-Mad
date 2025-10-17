from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .models import Ambiente, Dispositivo



#def home(request):
  #  """Página inicial"""
 #   return render(request, 'core/home.html')

def ambiente_detail(request, pk):
    ambiente = get_object_or_404(Ambiente, pk=pk)
    return render(request, 'core/ambiente_detail.html', {'ambiente': ambiente})



@login_required
def dashboard(request):
    """Dashboard principal para usuários autenticados"""
    return render(request, 'core/dashboard.html')

def dispositivo_detail(request, pk):
    dispositivo = get_object_or_404(Dispositivo, pk=pk)
    return render(request, 'core/dispositivo_detail.html', {'dispositivo': dispositivo})

def registro(request):
    """Página de registro de novos usuários"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')


class CustomLogoutView(LogoutView):
    next_page = 'login'
