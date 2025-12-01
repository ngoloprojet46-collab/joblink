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
from .models import Boutique
from .forms import BoutiqueForm




# Page d'accueil
def home(request):
    services = Service.objects.order_by('-date_publication')[:9]
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
def creer_boutique(request):
    # Seuls les prestataires peuvent créer une boutique
    if not hasattr(request.user, 'prestataire'):
        messages.error(request, "Seuls les prestataires peuvent créer une boutique.")
        return redirect('home')

    # Vérifie si le prestataire a déjà une boutique
    if hasattr(request.user.prestataire, 'boutique'):
        messages.info(request, "Vous avez déjà une boutique.")
        return redirect('modifier_boutique')

    if request.method == 'POST':
        form = BoutiqueForm(request.POST, request.FILES)
        if form.is_valid():
            boutique = form.save(commit=False)
            boutique.prestataire = request.user.prestataire
            boutique.save()
            messages.success(request, "Votre boutique a été créée avec succès ✅")
            return redirect('detail_boutique', boutique.id)
    else:
        form = BoutiqueForm()

    return render(request, 'core/creer_boutique.html', {'form': form})


def boutiques_list(request):
    query = request.GET.get('q')  # On récupère le paramètre 'q' dans l'URL
    if query:
        boutiques = Boutique.objects.filter(nom__icontains=query)  # Recherche insensible à la casse
    else:
        boutiques = Boutique.objects.all()
    return render(request, 'core/boutiques_list.html', {'boutiques': boutiques, 'query': query})


def boutique_detail(request, boutique_id):
    boutique = Boutique.objects.get(id=boutique_id)
    services = Service.objects.filter(boutique=boutique)
    return render(request, 'core/boutique_detail.html', {'boutique': boutique, 'services': services})

def detail_boutique(request, boutique_id):
    boutique = get_object_or_404(Boutique, id=boutique_id)
    services = Service.objects.filter(prestataire=boutique.prestataire)

    return render(request, "core/detail_boutique.html", {
        "boutique": boutique,
        "services": services
    })


    return render(request, 'boutique/detail_boutique.html', context)



@login_required
def modifier_boutique(request):
    try:
        boutique = Boutique.objects.get(prestataire=request.user.prestataire)
    except Boutique.DoesNotExist:
        return redirect('creer_boutique')

    if request.method == 'POST':
        form = BoutiqueForm(request.POST, request.FILES, instance=boutique)
        if form.is_valid():
            form.save()
            return redirect('detail_boutique', boutique.id)
    else:
        form = BoutiqueForm(instance=boutique)

    return render(request, 'core/modifier_boutique.html', {'form': form})



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
        messages.error(request, "Profil prestataire introuvable.")
        return redirect('home')

    services = Service.objects.filter(prestataire=prestataire)
    commandes = Commande.objects.filter(service__prestataire=prestataire)

    # 🔥 récupérer uniquement LA DERNIÈRE notification
    derniere_notification = Notification.objects.filter(
        user=request.user
    ).order_by('-date').first()

    context = {
        'prestataire': prestataire,
        'services': services,
        'commandes': commandes,
        'derniere_notification': derniere_notification,
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
    return redirect('mes_notifications')

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

    # Vérifie que c’est bien le prestataire
    if commande.service.prestataire.user != request.user:
        messages.error(request, "Action non autorisée.")
        return redirect('tableau_prestataire')

    commande.statut = 'acceptee'
    commande.save()

    demandeur_user = commande.demandeur.user

    # 🔥 Téléphone du demandeur
    numero_demandeur = demandeur_user.phone if demandeur_user.phone else "Numéro non renseigné"

    # 🔥 Notification envoyée au prestataire
    Notification.objects.create(
        user=commande.service.prestataire.user,   # destinataire = prestataire
        prestataire=commande.service.prestataire,
        message=(
            f"Nouvelle commande acceptée pour le service « {commande.service.titre} ».\n"
            f"Le demandeur : {demandeur_user.username}\n"
            f"Téléphone : {numero_demandeur}"
        )
    )

    # 🔥 Notification envoyée au demandeur (déjà existante chez toi)
    Notification.objects.create(
        user=demandeur_user,
        prestataire=commande.service.prestataire,
        message=(
            f"Votre commande pour « {commande.service.titre} » a été acceptée !\n"
            f"Contactez le prestataire au : {commande.service.prestataire.telephone}"
        )
    )

    messages.success(request, "Commande acceptée et notifications envoyées.")
    return redirect('tableau_prestataire')

@login_required
def liste_notifications_prestataire(request):
    # 🔥 Récupérer uniquement les notifications destinées au prestataire connecté
    notifications = Notification.objects.filter(
        user=request.user,  # destinataire = l'utilisateur connecté
        prestataire__user=request.user  # facultatif si tu veux t'assurer que c'est bien un prestataire
    ).order_by('-date')

    context = {
        'notifications': notifications
    }
    return render(request, 'liste_notifications_prestataire.html', context)

@login_required
def supprimer_notification_prestataire(request, notif_id):
    try:
        prestataire = Prestataire.objects.get(user=request.user)
    except Prestataire.DoesNotExist:
        messages.error(request, "Vous n'êtes pas prestataire.")
        return redirect('dashboard')

    notif = get_object_or_404(Notification, id=notif_id, prestataire=prestataire)
    notif.delete()

    messages.success(request, "Notification supprimée ✔")
    return redirect('liste_notifications_prestataire')



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
            return redirect('avis_merci')
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

def avis_merci(request):
    return render(request, "avis_merci.html")



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

def reset_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('reset_password')

        try:
            user = User.objects.get(email=email)
            user.password = make_password(password1)  # hash le mot de passe
            user.save()
            messages.success(request, "Mot de passe réinitialisé avec succès !")
            return redirect('login')  # redirige vers la page de connexion
        except User.DoesNotExist:
            messages.error(request, "Utilisateur introuvable avec cet email.")
            return redirect('reset_password')

    return render(request, 'core/reset_password.html')


