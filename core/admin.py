from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Prestataire, Demandeur, Service, Commande, Paiement,
    Notification, Abonnement, Avis, Boutique
)

from django.utils.html import format_html
from django.urls import reverse

# ---------------------
# Historique (LogEntry)
# ---------------------
admin.site.register(LogEntry)


# ----------------------------------------------------
# Gestion du User (CustomUserAdmin remplacé proprement)
# ----------------------------------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': (
            'first_name', 'last_name', 'email', 'phone', 'photo'
        )}),
        ('Rôle', {'fields': ('role',)}),
        ('Permissions', {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
        )}),
        ('Dates importantes', {'fields': (
            'last_login', 'date_joined'
        )}),
    )

    list_display = ('username', 'role', 'email', 'phone', 'is_staff')
    search_fields = ('username', 'email', 'phone')


@admin.register(Prestataire)
class PrestataireAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'competence',
        'experience',
        'localisation',
        'note_moyenne',
        'date_debut_abonnement',
        'date_fin_abonnement',
        'abonnement_actif',
        'creer_abonnement_bouton',   # 👉 AJOUT
    )

    search_fields = ('user__username', 'competence', 'localisation')

    # Récupérer date_debut depuis Abonnement
    def date_debut_abonnement(self, obj):
        try:
            return obj.user.abonnement.date_debut
        except:
            return "—"
    date_debut_abonnement.short_description = "Début abonnement"

    # Récupérer date_fin depuis Abonnement
    def date_fin_abonnement(self, obj):
        try:
            return obj.user.abonnement.date_fin
        except:
            return "—"
    date_fin_abonnement.short_description = "Fin abonnement"

    # Voir si l’abonnement est actif
    def abonnement_actif(self, obj):
        try:
            return "Oui" if obj.user.abonnement.est_actif() else "Non"
        except:
            return "—"
    abonnement_actif.short_description = "Abonnement actif ?"

    # 👉 Bouton "Créer abonnement"
    def creer_abonnement_bouton(self, obj):
        # S'il n'a PAS d'abonnement → afficher bouton
        abonnement = getattr(obj.user, 'abonnement', None)
        if abonnement is None:
            url = reverse("admin:core_abonnement_add") + f"?user={obj.user.id}"
            return format_html(
                '<a class="button" style="padding:3px 8px; background:#28a745; color:white; border-radius:3px;" href="{}">Créer</a>',
                url
            )
        
        # Sinon → afficher un texte
        return "Déjà créé"
    
    creer_abonnement_bouton.short_description = "Créer abonnement"

    def response_add(self, request, obj, post_url_continue=None):
        # Rester sur la page d'ajout après l'enregistrement
        request.POST = request.POST.copy()
        request.POST["_addanother"] = "yes"
        return super().response_add(request, obj, post_url_continue)

# ---------------------
# Gestion des Demandeurs
# ---------------------
@admin.register(Demandeur)
class DemandeurAdmin(admin.ModelAdmin):
    list_display = ('user', 'adresse')
    search_fields = ('user__username', 'adresse')


# ---------------------
# Avis
# ---------------------
@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('nom', 'message', 'date')
    list_filter = ('date',)
    search_fields = ('nom', 'message')


# ---------------------
# Boutiques
# ---------------------
@admin.register(Boutique)
class BoutiqueAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prestataire', 'categorie', 'date_creation')
    list_filter = ('categorie', 'date_creation')
    
    # recherche dans prestataire.user.username
    search_fields = ('nom', 'prestataire__user__username')

    readonly_fields = ('date_creation',)

    fieldsets = (
        ("Informations principales", {
            "fields": ("prestataire", "nom", "description", "categorie")
        }),
        ("Image de la boutique", {
            "fields": ("image",),
        }),
        ("Dates", {
            "fields": ("date_creation",),
        }),
    )


# ---------------------
# Abonnements
# ---------------------


@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'date_debut',
        'date_fin',
        'actif',
        'afficher_preuve_paiement',
        'renouveler_abonnement_bouton'
    )
    readonly_fields = ('date_debut',)
    search_fields = ('user__username', 'user__email')

    # Filtrer pour ne voir que les prestataires
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user__role='prestataire')

    # Action globale
    actions = ['prolonger_abonnement']

    def prolonger_abonnement(self, request, queryset):
        for abonnement in queryset:
            abonnement.prolonger(30)
        self.message_user(request, "Abonnement(s) prolongé(s) de 30 jours")
    prolonger_abonnement.short_description = "Prolonger les abonnements sélectionnés de 30 jours"

    # Bouton individuel
    def renouveler_abonnement_bouton(self, obj):
        url = reverse('renouveler_abonnement_admin', args=[obj.id])
        return format_html(
            '<a class="button" style="padding:3px 8px; background-color:#0d6efd; color:white; border-radius:3px; text-decoration:none;" href="{}">Renouveler</a>',
            url
        )
    renouveler_abonnement_bouton.short_description = 'Renouveler'

    # ✅ Méthode pour afficher la preuve
    def afficher_preuve_paiement(self, obj):
        if obj.preuve_paiement:
            return format_html('<a href="{}" target="_blank">Voir</a>', obj.preuve_paiement.url)
        return "Aucune preuve"
    afficher_preuve_paiement.short_description = "Preuve de paiement"
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.filter(user__role='prestataire')
        return qs.order_by('-preuve_paiement', '-date_debut')  # Preuve d’abord, puis récents





    # ---------------------
# Gestion des Services
# ---------------------
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'prestataire', 'categorie', 'ville', 'date_publication')
    search_fields = ('titre', 'categorie', 'ville', 'prestataire__user__username')
    list_filter = ('categorie', 'ville', 'date_publication')


# ---------------------
# Gestion des Commandes
# ---------------------
from django.contrib import admin
from .models import Commande

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = (
        'demandeur',
        'service', 
        'prestataire', 
        'telephone_service',   # ← téléphone du service
        'telephone_prestataire',  # ← téléphone du prestataire
        'statut',
        'date_commande'
        
    )
    
    list_display_links = ('service',)   # rend le service cliquable
    
    search_fields = (
        'demandeur_user_username',
        'service__titre',
        'service_prestataireuser_username'
    )
    list_filter = ('statut', 'date_commande')

    # Méthode pour afficher le prestataire
    def prestataire(self, obj):
        return obj.service.prestataire.user.username
    prestataire.short_description = "Prestataire"

    # Méthode pour afficher le téléphone du prestataire
    def telephone_prestataire(self, obj):
        return obj.service.prestataire.telephone
    telephone_prestataire.short_description = "Téléphone Prestataire"

    # Méthode pour afficher le téléphone du service
    def telephone_service(self, obj):
        return obj.service.telephone
    telephone_service.short_description = "Téléphone Service"

# ---------------------
# Paiements
# ---------------------
@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('commande', 'montant', 'date_paiement', 'statut')
    search_fields = ('commande_service_titre',)
    list_filter = ('statut', 'date_paiement')


# ---------------------
# Notifications
# ---------------------
from django.contrib import admin
from django.db.models import Q
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'prestataire', 'message', 'lue', 'date')
    search_fields = ('user__username', 'message')
    list_filter = ('lue', 'date')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Filtrer uniquement les notifications de commandes
        return qs.filter(Q(message__icontains='commander') | Q(message__icontains='acceptée'))