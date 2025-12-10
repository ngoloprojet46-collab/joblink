from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Prestataire, Demandeur, Service, Commande, Paiement,
    Notification, Abonnement, Avis, Boutique
)

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


# ---------------------
# Gestion des Prestataires
# ---------------------
@admin.register(Prestataire)
class PrestataireAdmin(admin.ModelAdmin):
    list_display = ('user', 'competence', 'experience', 'localisation', 'note_moyenne')
    search_fields = ('user__username', 'competence', 'localisation')


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
    search_fields = ('nom', 'prestataire_user_username')

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
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Abonnement

@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_debut', 'date_fin', 'actif', 'preuve_paiement', 'renouveler_abonnement_bouton')
    readonly_fields = ('date_debut',)
    search_fields = ('user_username', 'user_email')

    # Filtrer pour ne voir que les prestataires
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user__role='prestataire')

    # Action globale (multi-sélection) pour prolonger
    actions = ['prolonger_abonnement']

    def prolonger_abonnement(self, request, queryset):
        for abonnement in queryset:
            abonnement.prolonger(30)
        self.message_user(request, "Abonnement(s) prolongé(s) de 30 jours")
    prolonger_abonnement.short_description = "Prolonger les abonnements sélectionnés de 30 jours"

    # Bouton individuel dans la liste
    def renouveler_abonnement_bouton(self, obj):
        url = reverse('renouveler_abonnement_admin', args=[obj.id])
        return format_html(
            '<a class="button" style="padding:3px 8px; background-color:#0d6efd; color:white; border-radius:3px; text-decoration:none;" href="{}">Renouveler</a>',
            url
        )
    renouveler_abonnement_bouton.short_description = 'Renouveler'
