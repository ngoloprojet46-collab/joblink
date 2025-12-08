from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import detail_commande, profil_view
from . import views_admin

from .views import (
    creer_boutique,
    boutiques_emploi,
    boutiques_vente,
    # ... autres vues
)


urlpatterns = [

    #path('test-email/', views.test_email, name='test_email'),


    path('demandeur/boite-messages/', views.boite_messages_demandeur, name='boite_messages_demandeur'),
    path(
    'demandeur/conversation/<int:service_id>/<int:prestataire_id>/',
    views.conversation_demandeur,
    name='conversation_demandeur'
),

    path('message/supprimer/<int:message_id>/',
     views.supprimer_message,
     name='supprimer_message'),

    path('prestataire/messages/', views.boite_messages_prestataire, name='boite_messages_prestataire'),
    path('prestataire/messages/<int:message_id>/', views.conversation_prestataire, name='conversation_prestataire'),
    path('prestataire/messages/<int:message_id>/supprimer/', views.supprimer_message_prestataire, name='supprimer_message_prestataire'),


    path('service/<int:service_id>/message/', views.envoyer_message, name='envoyer_message'),
    path('message/<int:message_id>/repondre/', views.repondre_message, name='repondre_message'),

    path('reset-password/', views.reset_password, name='reset_password'),

    path('admin-dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),

    path('profil/', profil_view, name='profil'),

    # Authentification
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),


    # Tableau de bord
    path('dashboard/', views.redirection_dashboard, name='dashboard'),
    path('tableau-prestataire/', views.tableau_prestataire, name='tableau_prestataire'),
    path('tableau-demandeur/', views.tableau_demandeur, name='tableau_demandeur'),

    # Notifications
    path('notifications/', views.mes_notifications, name='mes_notifications'),
    path('notification/<int:notification_id>/lue/', views.marquer_notification_lue, name='marquer_notification_lue'),
    path('notifications/tout-lu/', views.tout_marquer_lu, name='tout_marquer_lu'),
    path('notification/<int:notification_id>/supprimer/', views.supprimer_notification, name='supprimer_notification'),
    path('notification/voir-prestataire/<int:notif_id>/', views.voir_prestataire_depuis_notification, name='voir_prestataire_depuis_notification'),

    # Prestataire
    path('prestataire/<int:prestataire_id>/', views.prestataire_detail, name='prestataire_detail'),

    # Services
    path('', views.home, name='home'),
    path('services/feed/', views.services_feed, name='services_feed'), # nouvelle vue
    path('services/', views.service_list, name='service_list'),
    path('services/<int:pk>/', views.service_detail, name='service_detail'),
    path('add-service/', views.add_service, name='add_service'),
    path('search/', views.quick_search, name='quick_search'),
    path('service/modifier/<int:service_id>/', views.modifier_service, name='modifier_service'),
    path('service/supprimer/<int:service_id>/', views.supprimer_service, name='supprimer_service'),
    path('service/<int:service_id>/commander/', views.commander_service, name='commander_service'),

    # Commandes
    path('commande/<int:commande_id>/', detail_commande, name='detail_commande'),
    path('commande/<int:commande_id>/accepter/', views.accepter_commande, name='accepter_commande'),
    path('commande/<int:commande_id>/terminer/', views.terminer_commande, name='terminer_commande'),
    path('commande/<int:commande_id>/annuler/', views.annuler_commande, name='annuler_commande'),
    path('commande/<int:commande_id>/supprimer/', views.supprimer_commande, name='supprimer_commande'),
    path('commande/<int:commande_id>/supprimer_prestataire/', views.supprimer_commande_prestataire, name='supprimer_commande_prestataire'),

    path('abonnement/expire/', views.abonnement_expire, name='abonnement_expire'),
    path('abonnement/', views.gerer_abonnement, name='gerer_abonnement'),

    # Mot de passe oublié
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='password_reset.html'),
         name='password_reset'),

    path('password_reset_done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),

    path('commenter/', views.commenter, name='commenter'),
    path('avis/', views.avis_list, name='avis_list'),
    path('commentaire/delete/<int:avis_id>/', views.avis_delete, name='avis_delete'),
    path('commentaire/delete_all/', views.avis_delete_all, name='avis_delete_all'),

    path('avis/admin/', views.avis_admin, name='avis_admin'),
    path('avis/toggle/<int:avis_id>/', views.toggle_public, name='toggle_public'),
    path('avis/toggle/<int:avis_id>/', views.toggle_avis, name='toggle_avis'),
    path('avis/merci/', views.avis_merci, name='avis_merci'),

    
    path('boutique/creer/', views.creer_boutique, name='creer_boutique'),
    path('boutique/modifier/', views.modifier_boutique, name='modifier_boutique'),
    path('boutique/<int:boutique_id>/', views.detail_boutique, name='detail_boutique'),
    path('boutique/<int:boutique_id>/', views.boutique_detail, name='boutique_detail'),

    path("boutiques/emploi/", views.boutiques_emploi, name="boutiques_emploi"),
    path("boutiques/vente/", views.boutiques_vente, name="boutiques_vente"),

   

     # Notifications Prestataire
    path('prestataire/notifications/', views.liste_notifications_prestataire, name='liste_notifications_prestataire'),
    path('prestataire/notifications/<int:notif_id>/supprimer/', views.supprimer_notification_prestataire, name='supprimer_notification_prestataire'),

]

