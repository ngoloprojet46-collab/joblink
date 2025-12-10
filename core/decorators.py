from django.shortcuts import redirect
from django.utils import timezone
from .models import Abonnement
from functools import wraps

def abonnement_actif_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # 🔹 Si l'utilisateur n'est pas connecté → login
        if not request.user.is_authenticated:
            return redirect('login')

        # 🔹 Le superuser n'a JAMAIS besoin d'un abonnement
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # 🔹 Vérifier si l'utilisateur a un abonnement
        try:
            abonnement = request.user.abonnement
        except Abonnement.DoesNotExist:
            return redirect('gerer_abonnement')

        # 🔹 Vérifier si l'abonnement est actif et non expiré
        if not abonnement.actif or abonnement.date_fin < timezone.now().date():
            return redirect('gerer_abonnement')

        return view_func(request, *args, **kwargs)

    return wrapper
