from django.db import models
from django.conf import settings

class Subscriber(models.Model):

    STATUS_CHOICES = [

        ('active', 'Active'),

        ('unsubscribed', 'Unsubscribed'),

        ('bounced', 'Bounced'),

        ('complained', 'Complained'),

        ('blocklisted', 'Blocklisted'),

    ]

    email = models.EmailField(unique=True)

    name = models.CharField(max_length=100, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

class Segment(models.Model):

    TYPE_CHOICES = [

        ('public', 'Public'),

        ('private', 'Private'),

        ('temporary', 'Temporary'),

    ]

    OPT_IN_CHOICES = [

        ('single', 'Single opt-in'),

        ('double', 'Double opt-in'),

    ]

    name = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='private')

    optin = models.CharField(max_length=10, choices=OPT_IN_CHOICES, default='single')

    tags = models.JSONField(blank=True, null=True)
    subscribers = models.ManyToManyField(Subscriber, related_name='segments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name