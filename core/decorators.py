from django.shortcuts import redirect
from django.utils import timezone
from .models import Abonnement

def abonnement_actif_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        try:
            abonnement = Abonnement.objects.get(user=request.user)
        except Abonnement.DoesNotExist:
            return redirect('gerer_abonnement')  # Redirection si pas d’abonnement

        # Si abonnement expiré
        if not abonnement.actif or abonnement.date_fin < timezone.now().date():
            return redirect('gerer_abonnement')

        return view_func(request, *args, **kwargs)

    return wrapper