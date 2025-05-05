from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import SignUpForm

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Vous avez été connecté avec succès.")
            return redirect('home')
        else:
            messages.error(request, "Identifiants invalides, veuillez réessayer.")
            return redirect('login')
            
    return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # Log in user
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, 'Le compte a été créé pour ' + username)
            return redirect('home')
        else: 
            messages.success(request, 'Erreur lors de la création de votre compte. Veuillez réessayer.')
            return redirect('register')
    else:
        return render(request, 'register.html', {'form': form})