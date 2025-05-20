import base64
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from .forms import SignUpForm, UpdateProfileForm
from .models import Utilisateur
from cart.cart import Cart
from offers.models import Offre
import json
from django.contrib.auth.decorators import login_required
import pyotp # type: ignore
import io
import qrcode # type: ignore

# 2FA
@login_required
def activate_2fa(request):
    utilisateur = request.user.utilisateur
    # Si 2FA déjà activée
    if utilisateur.is_2fa_enabled:
        return redirect('verify_2fa')
    # Génère un secret temporaire stocké uniquement en session
    secret = pyotp.random_base32()
    request.session['temp_totp_secret'] = secret

    return redirect('verify_2fa')

@login_required
def verify_2fa(request):
    utilisateur = request.user.utilisateur
    qr_image = None
    secret = request.session.get('temp_totp_secret') or utilisateur.totp_secret

    if secret:
        totp = pyotp.TOTP(secret)
        otp_url = totp.provisioning_uri(name=request.user.email, issuer_name="JO24")

        qr = qrcode.make(otp_url)
        buffer = io.BytesIO()
        qr.save(buffer, format='PNG')
        qr_image = base64.b64encode(buffer.getvalue()).decode()

    if request.method == 'POST':
        code = request.POST.get('code')

        if secret:
            totp = pyotp.TOTP(secret)
            if totp.verify(code, valid_window=1):
                utilisateur.totp_secret = secret
                utilisateur.is_2fa_verified = True
                utilisateur.is_2fa_enabled = True
                utilisateur.save()

                request.session['is_2fa_verified'] = True
                request.session.pop('temp_totp_secret', None)
                return redirect('home')
            else:
                messages.error(request, "Code incorrect.")
        else:
            messages.error(request, "Erreur : secret manquant.")

    return render(request, 'verify_2fa.html', {
        'qr_image': qr_image,
        'manual_code': secret,
    })

# Login, Logout, Register

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            cart = Cart(request)

            current_user = Utilisateur.objects.get(user=user)
            saved_cart = current_user.old_cart

            if saved_cart:
                try:
                    converted_cart = json.loads(saved_cart)
                    for key, value in converted_cart.items():
                        parts = key.split('_')
                        if len(parts) == 2:
                            product_id, type_billet = parts
                            try:
                                product = Offre.objects.get(id=product_id)
                                cart.cart[key] = {
                                    'id': product_id,
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

            # 🔐 Gérer la redirection 2FA
            if hasattr(user, 'utilisateur') and user.utilisateur.totp_secret:
                request.session['is_2fa_verified'] = False
                return redirect('verify_2fa')

            messages.success(request, "Vous avez été connecté avec succès.")
            return redirect('home')
        else:
            messages.error(request, "Identifiants invalides.")
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
    
@login_required
def update_profile(request):
    user = request.user
    utilisateur = Utilisateur.objects.get(user=user)

    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=user, utilisateur_instance=utilisateur)
        if form.is_valid():
            form.save(utilisateur_instance=utilisateur)
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('home')
    else:
        form = UpdateProfileForm(instance=user, utilisateur_instance=utilisateur)

    return render(request, 'update_profile.html', {'form': form})