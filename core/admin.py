from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import UserAdmin
from .models import User, Prestataire, Demandeur, Service, Commande, Paiement, Notification, Abonnement


# --- Activation de l'historique dans l'admin ---
admin.site.register(LogEntry)


# --- Admin du User personnalisé ---
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'phone', 'photo')}),
        ('Rôle', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'role', 'email', 'phone', 'is_staff')
    search_fields = ('username', 'email', 'phone')


# --- Enregistrement des autres modèles ---
admin.site.register(Prestataire)
admin.site.register(Demandeur)
admin.site.register(Service)
admin.site.register(Commande)
admin.site.register(Paiement)
admin.site.register(Notification)
admin.site.register(Abonnement)

from django.contrib import admin
from .models import Avis

@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('nom', 'message', 'date')
    list_filter = ('date',)
    search_fields = ('nom', 'message')

