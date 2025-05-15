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

def activate_2fa(request):
    utilisateur = request.user.utilisateur

    # Si 2FA est déjà activé, on redirige vers la vérification
    if utilisateur.totp_secret:
        return redirect('verify_2fa')

    # Génération et enregistrement du secret
    secret = pyotp.random_base32()
    utilisateur.totp_secret = secret
    utilisateur.save()

    # Stockage temporaire du secret dans la session
    request.session['totp_secret'] = secret

    # Redirige automatiquement vers le formulaire de vérification
    return redirect('verify_2fa')


@login_required
def verify_2fa(request):
    utilisateur = request.user.utilisateur
    qr_image = None
    secret = utilisateur.totp_secret or request.session.get('totp_secret')

    if secret:
        totp = pyotp.TOTP(secret)
        otp_url = totp.provisioning_uri(name=request.user.email, issuer_name="JO24")

        qr = qrcode.make(otp_url)
        buffer = io.BytesIO()
        qr.save(buffer, format='PNG')
        qr_image = base64.b64encode(buffer.getvalue()).decode()  # image encodée en base64

    if request.method == 'POST':
        code = request.POST.get('code')

        if utilisateur.totp_secret:
            totp = pyotp.TOTP(utilisateur.totp_secret)
            # Vérification du code TOTP
            if totp.verify(code, valid_window=1):
                utilisateur.is_2fa_verified = True
                utilisateur.save()
                request.session['is_2fa_verified'] = True
                request.session.pop('totp_secret', None)
                return redirect('home')
            else:
                messages.error(request, "Code incorrect.")
        else:
            messages.error(request, "2FA non activé.")

    return render(request, 'verify_2fa.html', {
        'qr_image': qr_image,
        'manual_code': secret,
    })

# Login, Logout, Register

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

            # 🔐 Si 2FA activé, on réinitialise la vérif
            if hasattr(user, 'utilisateur') and user.utilisateur.totp_secret:
                request.session['is_2fa_verified'] = False
                return redirect('verify_2fa')
        
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