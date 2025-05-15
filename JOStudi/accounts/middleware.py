from django.shortcuts import redirect
from django.contrib.auth import logout

class TwoFactorRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        path = request.path
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

        utilisateur = getattr(request.user, 'utilisateur', None)
        if utilisateur and utilisateur.is_2fa_enabled:
            if not request.session.get('is_2fa_verified'):
                # Protection redémarrage
                logout(request)
                return redirect('/accounts/login')

        return self.get_response(request)