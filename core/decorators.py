from django.shortcuts import redirect
from django.utils import timezone
from core.models import Abonnement

def abonnement_actif_required(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            abonnement = Abonnement.objects.get(user=request.user)
            if abonnement.date_fin < timezone.now():
                return redirect('abonnement_expire')
        except Abonnement.DoesNotExist:
            return redirect('abonnement_expire')

        return view_func(request, *args, **kwargs)
    return wrapper
