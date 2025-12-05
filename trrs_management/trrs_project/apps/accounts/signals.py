"""
Signals para la app de accounts
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea automáticamente un perfil cuando se crea un usuario
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Guarda el perfil cuando se actualiza el usuario
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
