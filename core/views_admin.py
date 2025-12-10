from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import User, Service, Commande
from django.shortcuts import redirect

@staff_member_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_services = Service.objects.count()
    total_commandes = Commande.objects.count()
    prestataires = User.objects.filter(role='prestataire').count()
    demandeurs = User.objects.filter(role='demandeur').count()

    context = {
        'total_users': total_users,
        'total_services': total_services,
        'total_commandes': total_commandes,
        'prestataires': prestataires,
        'demandeurs': demandeurs,
    }
    return render(request, 'admin_dashboard.html', context)


def redirect_after_login(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.role == 'prestataire':
        return redirect('prestataire_dashboard')
    else:
        return redirect('demandeur_dashboard')

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Abonnement

def renouveler_abonnement_admin(request, abonnement_id):
    abonnement = get_object_or_404(Abonnement, id=abonnement_id)
    abonnement.prolonger(30)
    messages.success(request, f"L'abonnement de {abonnement.user.username} a été prolongé de 30 jours.")
    return redirect('/admin/core/abonnement/')  # revenir à la liste admin