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
@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_utilisateur', 'date_debut', 'date_fin', 'actif')
    list_filter = ('type_utilisateur', 'actif')

    # Correction importante
    search_fields = ('user__username', 'user__email')

    readonly_fields = ('date_debut',)

    actions = ['prolonger_abonnement']

    def prolonger_abonnement(self, request, queryset):
        for abonnement in queryset:
            abonnement.prolonger(30)
        self.message_user(request, "Abonnement(s) prolongé(s) de 30 jours")
    prolonger_abonnement.short_description = "Prolonger de 30 jours"


# ---------------------
# Services, Commandes, Paiements, Notifications
# ---------------------
admin.site.register(Service)
admin.site.register(Commande)
admin.site.register(Paiement)
admin.site.register(Notification)
