from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ServiceForm
from .models import Prestataire, Demandeur
from django.contrib.admin.views.decorators import staff_member_required
from .models import User
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Service, Commande, Notification
from core.decorators import abonnement_actif_required
from datetime import timedelta, date
from .models import Abonnement
from django.contrib.auth.decorators import login_required
from .forms import ProfilUpdateForm
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import AvisForm
from .models import Avis
from django.shortcuts import redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required


# Page d'accueil
def home(request):
    services = Service.objects.order_by('-date_publication')[:6]
    default_bg = "https://res.cloudinary.com/dxndciemg/image/upload/v1763993564/job1_nlecfm.jpg"
    # Prépare une liste de tuples (service, bg_url)
    slides = []
    for s in services:
        if getattr(s, 'image') and getattr(s.image, 'url', None):
            bg = s.image.url
        else:
            bg = default_bg
        slides.append({'service': s, 'bg_url': bg})

    context = {
        'slides': slides,
        'services': services,
        'user_role': request.user.role if request.user.is_authenticated else None
    }
    return render(request, 'core/home.html', context)


# Inscription utilisateur
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']

            # Création du profil selon le rôle choisi
            if role == 'prestataire':
                Prestataire.objects.create(user=user)
            else:
                Demandeur.objects.create(user=user)

            login(request, user)
            messages.success(request, "Inscription réussie ! Bienvenue sur JobLink 👋🏾")
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profil_view(request):
    if request.method == 'POST':
        form = ProfilUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour ✅")
            # 🔹 Redirection vers le dashboard selon le rôle
            if request.user.role == 'prestataire':
                return redirect('tableau_prestataire')
            else:
                return redirect('tableau_demandeur')
    else:
        form = ProfilUpdateForm(instance=request.user)

    return render(request, 'profil.html', {'form': form})


# Tableau de bord Prestataire
@login_required
def tableau_prestataire(request):
    try:
        prestataire = Prestataire.objects.get(user=request.user)
    except Prestataire.DoesNotExist:
        messages.error(request, "Aucun profil prestataire trouvé.")
        return redirect('home')

    services = Service.objects.filter(prestataire=prestataire)
    commandes = Commande.objects.filter(service__prestataire=prestataire)

    context = {
        'prestataire': prestataire,
        'services': services,
        'commandes': commandes,
    }
    return render(request, 'dashboard_prestataire.html', context)

# Tableau de bord Demandeur
@login_required
def tableau_demandeur(request):
    demandeur = get_object_or_404(Demandeur, user=request.user)

    # ✅ Correction ici : utiliser demandeur au lieu de client
    commandes = Commande.objects.filter(demandeur=demandeur).select_related('service__prestataire')

    notifications = Notification.objects.filter(user=request.user).order_by('-date')

    context = {
        'demandeur': demandeur,
        'commandes': commandes,
        'notifications': notifications,
    }
    return render(request, 'dashboard_demandeur.html', context)

@login_required
def marquer_notification_lue(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.lue = True
    notification.save()
    return redirect('tableau_demandeur')

@login_required
def tout_marquer_lu(request):
    Notification.objects.filter(user=request.user, lue=False).update(lue=True)
    return redirect('mes_notifications')

@login_required
def redirection_dashboard(request):
    user = request.user

    # Si l'utilisateur est un prestataire
    if hasattr(user, 'prestataire'):
        return redirect('tableau_prestataire')

    # Si l'utilisateur est un demandeur (client)
    elif hasattr(user, 'demandeur'):
        return redirect('tableau_demandeur')

    # Par défaut
    return redirect('home')


# Liste des services
def service_list(request):
    query = request.GET.get('q')
    ville = request.GET.get('ville')

    # Trier du plus récent au plus ancien
    services = Service.objects.all().order_by('-date_publication')

    if query:
        services = services.filter(
            Q(titre__icontains=query) | 
            Q(categorie__icontains=query)
        )

    if ville:
        services = services.filter(ville=ville)

    context = {
        'services': services,
        'query': query,
        'ville': ville,
        'villes': Service.VILLES_CI,
        'user_role': request.user.role if request.user.is_authenticated else None
    }
    return render(request, 'core/service_list.html', context)

# Détail d’un service
def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    return render(request, 'core/service_detail.html', {'service': service})


# Ajouter un service (prestataire)
@login_required
def add_service(request):
    # ✅ Seuls les prestataires peuvent ajouter un service
    if not hasattr(request.user, 'prestataire'):
        messages.error(request, "Seuls les prestataires peuvent ajouter un service.")
        return redirect('service_list')

    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.prestataire = request.user.prestataire
            service.save()
            messages.success(request, 'Votre service a été ajouté avec succès ✅')
            return redirect('service_list')
    else:
        form = ServiceForm()

    return render(request, 'core/add_service.html', {'form': form})


def quick_search(request):
    query = request.GET.get('q', '').strip()
    services = Service.objects.none()  # Aucun résultat par défaut

    if query:
        services = Service.objects.filter(
            Q(titre__icontains=query) |
            Q(categorie__icontains=query) |
            Q(description__icontains=query)
        )
    else:
        # Si aucun mot n'est recherché, on n'affiche rien (pas tous les services)
        services = Service.objects.none()

    return render(request, 'core/quick_search.html', {
        'services': services,
        'query': query,
    })

@login_required
def modifier_service(request, service_id):
    service = get_object_or_404(Service, id=service_id, prestataire__user=request.user)

    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Le service a été modifié avec succès ✅")
            return redirect('dashboard')
    else:
        form = ServiceForm(instance=service)

    return render(request, 'core/modifier_service.html', {'form': form})

@login_required
def supprimer_service(request, service_id):
    service = get_object_or_404(Service, id=service_id, prestataire__user=request.user)

    if request.method == 'POST':
        service.delete()
        messages.success(request, "Le service a été supprimé avec succès 🗑")
        return redirect('dashboard')

    return render(request, 'core/supprimer_service.html', {'service': service})

@login_required
def commander_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    # ✅ Vérifie si le demandeur connecté a déjà commandé ce service
    demandeur = getattr(request.user, 'demandeur', None)
    if not demandeur:
        messages.error(request, "Seuls les demandeurs peuvent commander un service.")
        return redirect('home')

    commande_existante = Commande.objects.filter(service=service, demandeur=demandeur).exists()
    if commande_existante:
        messages.warning(request, "Vous avez déjà commandé ce service ❗")
        return redirect('dashboard')

    # ✅ Création de la commande
    Commande.objects.create(service=service, demandeur=demandeur)
    messages.success(request, "Votre commande a été enregistrée avec succès ✅")
    return redirect('dashboard')

@login_required
def accepter_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)

    # Vérifie que c’est bien le prestataire du service qui accepte
    if commande.service.prestataire.user == request.user:
        commande.statut = 'acceptee'
        commande.save()

        # ✅ Création d'une notification pour le demandeur (avec lien prestataire)
        Notification.objects.create(
            user=commande.demandeur.user,  # destinataire = demandeur
            prestataire=commande.service.prestataire,  # 🔗 lien vers le prestataire
            message=(
                f"Votre commande pour le service « {commande.service.titre} » a été acceptée ! 🎉\n"
                f"Vous pouvez contacter le prestataire : {commande.service.prestataire.user.username} "
                f"au {commande.service.prestataire.telephone}."
            )
        )

        messages.success(request, "Commande acceptée et notification envoyée au demandeur ✅")
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accepter cette commande ❌")

    return redirect('dashboard')

@login_required
def mes_notifications(request):
    notifications_list = Notification.objects.filter(user=request.user).order_by('-date')
    paginator = Paginator(notifications_list, 5)  # 5 notifications par page
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    return render(request, 'notifications.html', {
        'notifications': notifications,
        'is_paginated': True,
        'paginator': paginator,
        'page_obj': notifications
    })

@login_required
def supprimer_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    messages.success(request, "Notification supprimée avec succès 🗑")
    return redirect('mes_notifications')

@login_required
def prestataire_detail(request, prestataire_id):
    prestataire = get_object_or_404(Prestataire, id=prestataire_id)
    return render(request, 'prestataire_detail.html', {'prestataire': prestataire})

@login_required
def terminer_commande(request, commande_id):
    prestataire = get_object_or_404(Prestataire, user=request.user)
    commande = get_object_or_404(Commande, id=commande_id, service__prestataire=prestataire)
    commande.statut = 'terminee'
    commande.save()
    messages.success(request, "Commande marquée comme terminée ✅")
    return redirect('dashboard')

@login_required
def annuler_commande(request, commande_id):
    prestataire = get_object_or_404(Prestataire, user=request.user)
    commande = get_object_or_404(Commande, id=commande_id, service__prestataire=prestataire)
    commande.statut = 'annulee'
    commande.save()
    messages.warning(request, "Commande annulée ❌")
    return redirect('dashboard')

@login_required
def detail_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, demandeur=request.user.demandeur)

    return render(request, 'detail_commande.html', {'commande': commande})

@login_required
def supprimer_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)

    # Vérifie que c’est bien le demandeur propriétaire de la commande
    if hasattr(request.user, 'demandeur') and commande.demandeur == request.user.demandeur:
        commande.delete()
        messages.success(request, "Commande supprimée avec succès 🗑")
    else:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cette commande ❌")

    return redirect('tableau_demandeur')

@login_required
def supprimer_commande_prestataire(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    
    # Vérification de l'appartenance
    if commande.service.prestataire.user == request.user:
        commande.delete()
        messages.success(request, "Commande supprimée avec succès 🗑")
    else:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cette commande ❌")
    
    return redirect('tableau_prestataire')


 # adapte le chemin selon ton app

@login_required
def voir_prestataire_depuis_notification(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)

    # ✅ Si la notification n'est pas encore lue, on la marque comme lue
    if not notif.lue:
        notif.lue = True
        notif.save()

    # ✅ Redirige ensuite vers la page du prestataire
    if notif.prestataire:
        return redirect('prestataire_detail', notif.prestataire.id)
    else:
        return redirect('mes_notifications')

def abonnement_expire(request):
    return render(request, 'core/abonnement_expire.html')

@login_required
def gerer_abonnement(request):
    # Récupérer ou créer l’abonnement de l’utilisateur
    abonnement, created = Abonnement.objects.get_or_create(user=request.user)

    # Vérifier si expiré
    if abonnement.date_fin < date.today():
        abonnement.actif = False
        abonnement.save()

    # Si l’utilisateur demande un renouvellement
    if request.method == "POST":
        abonnement.date_debut = date.today()
        abonnement.date_fin = abonnement.date_debut + timedelta(days=30)
        abonnement.actif = True
        abonnement.save()
        messages.success(request, "Votre abonnement a été renouvelé avec succès.")
        return redirect('gerer_abonnement')

    return render(request, "core/gerer_abonnement.html", {
        "abonnement": abonnement
    })

# Ajouter un commentaire
def commenter(request):
    if request.method == "POST":
        form = AvisForm(request.POST)
        if form.is_valid():
            avis = form.save(commit=False)
            if request.user.is_authenticated:
                avis.auteur = request.user
            avis.save()
            return redirect('avis_list')
    else:
        form = AvisForm()
    return render(request, 'commenter.html', {'form': form})


# Voir tous les commentaires
def avis_list(request):
    # Admin => voir tous les commentaires
    if request.user.is_staff:
        avis = Avis.objects.order_by('-date')
    else:
        # Utilisateur normal => voir seulement ceux qui sont publics
        avis = Avis.objects.filter(is_public=True).order_by('-date')

    return render(request, "avis_list.html", {"avis": avis})


@staff_member_required
def toggle_public(request, avis_id):
    avis = get_object_or_404(Avis, id=avis_id)
    avis.is_public = not avis.is_public  # inverse l’état
    avis.save()
    return redirect('avis_admin')


from django.contrib.auth.decorators import login_required

@login_required
def avis_delete(request, avis_id):
    avis = get_object_or_404(Avis, id=avis_id)

    # Autoriser uniquement si :
    # - l’utilisateur est staff (admin)
    # - OU l’utilisateur est l’auteur du commentaire
    if request.user.is_staff or avis.auteur == request.user:
        avis.delete()
        return redirect('avis_list')
    else:
        return HttpResponseForbidden("Vous n'avez pas le droit de supprimer ce commentaire.")

@staff_member_required
def avis_delete_all(request):
    Avis.objects.all().delete()
    return redirect('avis_list')

@staff_member_required
def avis_admin(request):
    avis = Avis.objects.order_by('-date')  # tous les avis
    return render(request, "avis_admin.html", {"avis": avis})


@staff_member_required
def toggle_avis(request, avis_id):
    avis = get_object_or_404(Avis, id=avis_id)
    avis.is_public = not avis.is_public
    avis.save()
    return redirect('avis')

