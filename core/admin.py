from django.contrib import admin
from .models import User, Service, Commande, Notification, Prestataire, Demandeur, Abonnement

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'phone')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'prix', 'prestataire', 'date_publication')
    list_filter = ('categorie',)
    search_fields = ('titre', 'prestataire_user_username')
    ordering = ('-date_publication',)

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('client', 'service', 'date_commande', 'statut')
    list_filter = ('statut',)
    search_fields = ('client_userusername', 'service_titre')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'date', 'lue')
    list_filter = ('lue',)
    search_fields = ('user__username', 'message')

admin.site.register(Prestataire)
admin.site.register(Demandeur)


# 🧭 Personnalisation globale du panneau d'administration
admin.site.site_header = "JobLink Administration"
admin.site.site_title = "JobLink Admin"
admin.site.index_title = "Bienvenue dans le tableau de bord JobLink"

from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.html import format_html

admin.site.site_header = "JobLink Administration"
admin.site.site_title = "JobLink Admin"
admin.site.index_title = "Bienvenue dans le tableau de bord JobLink"

# 💡 Pour ajouter ton logo dans l'en-tête
def joblink_logo():
    return format_html(
        '<img src="{}" alt="JobLink Logo" height="40" style="margin-right:10px;">',
        staticfiles_storage.url('core/img/logo-joblink.png')
    )

admin.site.site_header = "JobLink Administration"


# Register your models here.

@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_debut', 'date_fin', 'actif')

