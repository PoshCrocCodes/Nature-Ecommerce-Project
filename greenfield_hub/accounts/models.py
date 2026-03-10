from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('consumer', 'Consumer'),
        ('producer', 'Producer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='consumer')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    postcode = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True, help_text='Producer farm/business description')
    farm_name = models.CharField(max_length=200, blank=True, help_text='For producers only')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    newsletter_opt_in = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_terms = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def is_producer(self):
        return self.role == 'producer'

    def is_consumer(self):
        return self.role == 'consumer'

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
