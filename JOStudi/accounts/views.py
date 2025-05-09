from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import SignUpForm
from .models import Utilisateur
from cart.cart import Cart
from offers.models import Offre
import json

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Vider le panier session (invité) juste après login
        cart = Cart(request)
        cart.clear()  

        # Authentifier l'utilisateur
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            cart = Cart(request)

            # Récupérer le panier sauvegardé
            current_user = Utilisateur.objects.get(user__id=request.user.id)
            saved_cart = current_user.old_cart

            if saved_cart:
                try:
                    converted_cart = json.loads(saved_cart)
                    for key, value in converted_cart.items():
                        parts = key.split('_')
                        if len(parts) == 2:
                            product_id, type_billet = parts
                        else:
                            continue

                        try:
                            product = Offre.objects.get(id=product_id)
                            # Ajout sans fusionner avec ancien panier session
                            cart.cart[key] = {
                                'price': str(product.get_prix(type_billet)),
                                'quantity': int(value['quantity']),
                                'title': str(product.titre),
                                'type_billet': type_billet
                            }
                        except Offre.DoesNotExist:
                            continue
                    cart.session.modified = True
                except json.JSONDecodeError:
                    pass

            messages.success(request, "Vous avez été connecté avec succès.")
            return redirect('home')
        else:
            messages.error(request, "Identifiants invalides, veuillez réessayer.")
            return redirect('login')

    return render(request, 'login.html')



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