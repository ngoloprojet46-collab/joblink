from datetime import date
from django.shortcuts import redirect
from django.urls import reverse
from .models import Abonnement

class AbonnementMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response   # OBLIGATOIRE !

    def __call__(self, request):

        if request.user.is_authenticated:

            # URLs à ne pas bloquer
            exempt_urls = [
                reverse('gerer_abonnement'),
                reverse('abonnement_expire'),
                reverse('logout'),
            ]

            # Ne pas bloquer si l'utilisateur se trouve sur ces pages
            if request.path not in exempt_urls:

                try:
                    abonnement = Abonnement.objects.get(user=request.user)

                    # Vérifier expiration
                    if abonnement.date_fin < date.today():
                        abonnement.actif = False
                        abonnement.save()
                        return redirect('abonnement_expire')

                except Abonnement.DoesNotExist:
                    return redirect('gerer_abonnement')

        return self.get_response(request)
