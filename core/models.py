from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta, date
from django.conf import settings
from cloudinary.models import CloudinaryField


class User(AbstractUser):
    ROLE_CHOICES = (
        ('prestataire', 'Prestataire'),
        ('demandeur', 'Demandeur'),
    )

    SOURCE_CHOICES = [
        ('facebook', 'Facebook'),
        ('whatsapp', 'WhatsApp'),
        ('ami', 'Recommandation d’un ami'),
        ('ecole', 'École / Université'),
        ('tiktok', 'TikTok'),
        ('autre', 'Autre'),
    ]

    AVIS_CHOICES = [
        ('excellent', 'Excellent'),
        ('bon', 'Bon'),
        ('moyen', 'Moyen'),
        ('mauvais', 'Mauvais'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    photo = CloudinaryField("photo_profil", blank=True, null=True)

    # 🔥 NOUVEAUX CHAMPS MARKETING
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, blank=True, null=True)
    avis_plateforme = models.CharField(max_length=20, choices=AVIS_CHOICES, blank=True, null=True)
    suggestion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"



class Prestataire(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    competence = models.TextField()
    experience = models.PositiveIntegerField(default=0, help_text="Années d'expérience")
    localisation = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True, null=True)  # ✅ ajouté
    email = models.EmailField(blank=True, null=True)  # ✅ ajouté
    note_moyenne = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} ({self.localisation})"


class Demandeur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    adresse = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username
        
class Service(models.Model):
    VILLES_CI = [
        ("Abidjan", "Abidjan"),
        ("Bouaké", "Bouaké"),
        ("Daloa", "Daloa"),
        ("Yamoussoukro", "Yamoussoukro"),
        ("San-Pédro", "San-Pédro"),
        ("Korhogo", "Korhogo"),
        ("Man", "Man"),
        ("Gagnoa", "Gagnoa"),
    ]

    prestataire = models.ForeignKey(
        'Prestataire',
        on_delete=models.CASCADE,
        related_name='services'
    )
    titre = models.CharField(max_length=100)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    categorie = models.CharField(max_length=100)
    ville = models.CharField(max_length=50, choices=VILLES_CI, default="Abidjan")
    date_publication = models.DateTimeField(auto_now_add=True)
    disponible = models.BooleanField(default=True)

    image = CloudinaryField("image", blank=True, null=True)
    video = CloudinaryField(resource_type="video", blank=True, null=True)

    def __str__(self):
        return self.titre


class Commande(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    client = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    demandeur = models.ForeignKey(Demandeur, on_delete=models.CASCADE)
    date_commande = models.DateTimeField(auto_now_add=True)
    statut_choices = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]
    statut = models.CharField(max_length=20, choices=statut_choices, default='en_attente')

    def __str__(self):
        return f"Commande de {self.client.username if self.client else 'Inconnu'} pour {self.service}"


class Paiement(models.Model):
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=50)  # Wave, Orange Money, etc.
    date_paiement = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('effectue', 'Effectué'),
        ('echoue', 'Échoué'),
    ], default='en_attente')

    def __str__(self):
        return f"Paiement {self.id} - {self.statut}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prestataire = models.ForeignKey('Prestataire', on_delete=models.CASCADE, null=True, blank=True)  # Ajout
    message = models.TextField()
    lue = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif pour {self.user.username} - {self.message[:30]}"



from datetime import timedelta, date, datetime



from django.conf import settings


from django.db import models
from django.conf import settings
from datetime import date, timedelta

class Abonnement(models.Model):
    TYPE_CHOICES = (
        ('prestataire', 'Prestataire'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type_utilisateur = models.CharField(max_length=20, choices=TYPE_CHOICES, default='prestataire')
    date_debut = models.DateField(auto_now_add=True)
    date_fin = models.DateField(blank=True, null=True)
    actif = models.BooleanField(default=True)
    preuve_paiement = CloudinaryField('preuve de paiement', blank=True, null=True)
    note_admin = models.TextField(blank=True, null=True)  # Optionnel, pour commentaire admin

    def save(self, *args, **kwargs):
        # Sécurité : si ce n'est pas un prestataire, on force type_utilisateur à prestataire
        if self.user.role != 'prestataire':
            self.type_utilisateur = 'prestataire'

        # Création : ajouter 7 jours gratuits si nouvel abonnement
        if not self.id:
            self.date_debut = date.today()
            self.date_fin = self.date_debut + timedelta(days=7)
        self.actif = self.date_fin >= date.today()
        super().save(*args, **kwargs)

    def prolonger(self, jours=30):
        self.date_fin = max(self.date_fin, date.today()) + timedelta(days=jours)
        self.actif = True
        self.save()

    def est_actif(self):
        return self.actif and self.date_fin >= date.today()

    def __str__(self):
        username = getattr(self.user, 'username', 'Utilisateur')
        return f"Abonnement {username} ({'actif' if self.est_actif() else 'inactif'})"



class Avis(models.Model):
    nom = models.CharField(max_length=100)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_public = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.nom} - {self.date}"

class Boutique(models.Model):
    CATEGORIES = [
        ("emploi", "Boutique d'emploi"),
        ("vente", "Boutique de vente"),
    ]

    prestataire = models.OneToOneField(Prestataire, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    description = models.TextField()
    categorie = models.CharField(max_length=20, choices=CATEGORIES, default="emploi")
    # <-- remplace ImageField par CloudinaryField
    image = CloudinaryField("image_boutique", blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom


class ConversationMessage(models.Model):
    service = models.ForeignKey(
        'Service',
        on_delete=models.CASCADE,
        related_name='conversation_messages'
    )

    commande = models.ForeignKey(
        'Commande',
        on_delete=models.CASCADE,
        related_name='conversation_messages',
        null=True,
        blank=True
    )

    sender_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversation_messages_sent'
    )

    receiver_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversation_messages_received'
    )

    content = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    class Meta:
        ordering = ['date_sent']
        verbose_name = "Message de conversation"
        verbose_name_plural = "Messages de conversation"

    def __str__(self):
        return f"{self.sender_user.username} → {self.receiver_user.username} ({self.service.titre})"
