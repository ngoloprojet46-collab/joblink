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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
     # 🖼 Photo de profil avec Cloudinary
    photo = CloudinaryField("photo_profil", blank=True, null=True)


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
    prix = models.DecimalField(max_digits=10, decimal_places=2)
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


class Abonnement(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_debut = models.DateField(auto_now_add=True)
    date_fin = models.DateField(blank=True, null=True)
    actif = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Si nouvel abonnement
        if not self.id:
            self.date_debut = date.today()
            self.date_fin = self.date_debut + timedelta(days=30)

        # Vérifier si expiré
        if self.date_fin:
            self.actif = self.date_fin >= date.today()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Abonnement de {self.user.username} - {'Actif' if self.actif else 'Expiré'}"

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
