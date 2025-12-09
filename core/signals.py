from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Abonnement

@receiver(post_save, sender=User)
def creer_abonnement(sender, instance, created, **kwargs):
    if created:
        Abonnement.objects.create(
            user=instance,
            type_utilisateur=instance.role
        )
