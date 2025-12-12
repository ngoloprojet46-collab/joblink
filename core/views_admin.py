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
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from core.models import Abonnement

@staff_member_required
def renouveler_abonnement_admin(request, abonnement_id):
    abonnement = get_object_or_404(Abonnement, id=abonnement_id)
    
    # Prolonger l'abonnement
    abonnement.prolonger(30)
    
    # Supprimer la preuve de paiement si elle existe
    if abonnement.preuve_paiement:
        try:
            # Supprime le fichier de Cloudinary
            abonnement.preuve_paiement.delete()
        except Exception as e:
            messages.warning(request, f"Impossible de supprimer la preuve : {e}")
        abonnement.preuve_paiement = None
        abonnement.save()
    
    messages.success(request, f"L'abonnement de {abonnement.user.username} a été prolongé de 30 jours et la preuve de paiement a été supprimée.")
    return redirect(request.META.get('HTTP_REFERER', '/admin/'))


