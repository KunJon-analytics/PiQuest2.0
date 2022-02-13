from django.conf import settings
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from datetime import date

class User(AbstractUser):
    is_taker = models.BooleanField(default=True)
    is_master = models.BooleanField(default=False)
    is_project_manager = models.BooleanField(default=False)
    email = models.EmailField('email address', max_length=254, unique=True)

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=255, help_text="Your full name")
    image = models.ImageField(
        default='profile_default.jpg', upload_to='profile_pics')
    slug = models.SlugField(max_length=30, unique=True)
    about = models.TextField(default="A brief description about me")
    joined = models.DateTimeField("Date Joined", auto_now_add=True)
    wallet_address = models.CharField(
        max_length=35, help_text="Pi wallet address")
    telegram_id = models.CharField(max_length=100, null=True, blank=True, default="username",
                                   help_text="please input your correct telegram username to connect with friends, fellow quiz takers, and quiz masters")

    def __str__(self):
        return self.user.get_username()


class Payment(models.Model):
    transaction_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


def post_user_created_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


post_save.connect(post_user_created_signal, sender=User)
