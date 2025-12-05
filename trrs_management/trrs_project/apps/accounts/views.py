"""
Vistas para el sistema de autenticación
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .models import User, UserProfile


def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido, {user.get_full_name()}!')
                return redirect('dashboard:home')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """Vista del perfil del usuario"""
    user = request.user
    profile = user.profile

    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password_view(request):
    """Vista para cambiar contraseña"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        user = request.user

        if not user.check_password(old_password):
            messages.error(request, 'La contraseña actual es incorrecta.')
        elif new_password1 != new_password2:
            messages.error(request, 'Las nuevas contraseñas no coinciden.')
        elif len(new_password1) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
        else:
            user.set_password(new_password1)
            user.save()
            messages.success(request, 'Contraseña actualizada exitosamente.')
            return redirect('accounts:profile')

    return render(request, 'accounts/change_password.html')
