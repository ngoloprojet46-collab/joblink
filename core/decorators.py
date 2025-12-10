from django.shortcuts import redirect
from django.utils import timezone
from .models import Abonnement
from functools import wraps

def abonnement_actif_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # 🔹 Les demandeurs n'ont PAS besoin d'abonnement
        if hasattr(request.user, 'demandeur'):
            return view_func(request, *args, **kwargs)

        try:
            abonnement = request.user.abonnement
        except Abonnement.DoesNotExist:
            return redirect('gerer_abonnement')

        if not abonnement.actif or abonnement.date_fin < timezone.now().date():
            return redirect('gerer_abonnement')

        return view_func(request, *args, **kwargs)

    return wrapper
