from django.shortcuts import redirect
from django.urls import resolve
from django.contrib.auth import logout

class TwoFactorRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si pas connecté, rien à faire
        if not request.user.is_authenticated:
            return self.get_response(request)

        path = request.path

        # Chemins exemptés de 2FA
        exempt_paths = [
            '/accounts/login',
            '/accounts/logout/',
            '/accounts/register',
            '/accounts/verify-2fa/',
            '/accounts/activate-2fa/',
            '/admin/',
        ]

        if any(path.startswith(p) for p in exempt_paths):
            return self.get_response(request)

        # Protection contre boucle ou session perdue
        if (
            hasattr(request.user, 'utilisateur') and
            request.user.utilisateur.totp_secret and
            request.user.utilisateur.is_2fa_verified and
            not request.session.get('is_2fa_verified')
        ):
            # Pour éviter blocage lors de redémarrage serveur
            logout(request)
            return redirect('/accounts/login')

        # Rediriger vers la page de vérification si nécessaire
        if (
            hasattr(request.user, 'utilisateur') and
            request.user.utilisateur.totp_secret and
            not request.session.get('is_2fa_verified')
        ):
            return redirect('/accounts/verify-2fa/')

        return self.get_response(request)