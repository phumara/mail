from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
import json
from ckeditor_uploader.fields import RichTextUploadingField


class Media(models.Model):
    """Model to store uploaded media files"""
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class SMTPProvider(models.Model):
    """SMTP Provider configuration model"""

    PROVIDER_CHOICES = [
        ('gmail', 'Gmail'),
        ('outlook', 'Outlook/Hotmail'),
        ('yahoo', 'Yahoo Mail'),
        ('sendgrid', 'SendGrid'),
        ('mailgun', 'Mailgun'),
        ('ses', 'Amazon SES'),
        ('postmark', 'Postmark'),
        ('custom', 'Custom SMTP'),
    ]

    name = models.CharField(_('Provider Name'), max_length=100, unique=True)
    provider_type = models.CharField(_('Provider Type'), max_length=20, choices=PROVIDER_CHOICES)
    is_active = models.BooleanField(_('Active'), default=True)
    is_default = models.BooleanField(_('Default Provider'), default=False)

    # SMTP Settings
    host = models.CharField(_('SMTP Host'), max_length=255)
    port = models.IntegerField(_('SMTP Port'), default=587)
    use_tls = models.BooleanField(_('Use TLS'), default=True)
    use_ssl = models.BooleanField(_('Use SSL'), default=False)
    skip_tls_verify = models.BooleanField(_('Skip TLS Verification'), default=False)

    # Authentication
    username = models.CharField(_('Username'), max_length=255, blank=True)
    password = models.CharField(_('Password'), max_length=255, blank=True)

    # API Keys (for services like SendGrid, Mailgun, etc.)
    api_key = models.CharField(_('API Key'), max_length=255, blank=True)
    api_secret = models.CharField(_('API Secret'), max_length=255, blank=True)

    # Rate Limits
    emails_per_day = models.IntegerField(_('Daily Email Limit'), default=1000)
    emails_per_hour = models.IntegerField(_('Hourly Email Limit'), default=100)
    emails_per_second = models.IntegerField(_('Per Second Limit'), default=2)

    # Additional Settings
    from_email = models.EmailField(_('From Email'), validators=[EmailValidator()])
    from_name = models.CharField(_('From Name'), max_length=255, default='Mail System')
    reply_to_email = models.EmailField(_('Reply To'), blank=True, validators=[EmailValidator()])

    # Tracking
    total_sent = models.BigIntegerField(_('Total Emails Sent'), default=0)
    total_delivered = models.BigIntegerField(_('Total Delivered'), default=0)
    total_bounced = models.BigIntegerField(_('Total Bounced'), default=0)
    total_opened = models.BigIntegerField(_('Total Opened'), default=0)
    total_clicked = models.BigIntegerField(_('Total Clicked'), default=0)

    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    last_used = models.DateTimeField(_('Last Used'), null=True, blank=True)

    class Meta:
        verbose_name = _('SMTP Provider')
        verbose_name_plural = _('SMTP Providers')
        ordering = ['-is_active', 'name']

    def __str__(self):
        return f"{self.name} ({self.provider_type})"

    def save(self, *args, **kwargs):
        if self.is_default:
            # If this provider is set as default, ensure all others are not
            SMTPProvider.objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def get_delivery_rate(self):
        """Calculate delivery rate percentage"""
        if self.total_sent == 0:
            return 0
        return (self.total_delivered / self.total_sent) * 100

    def is_within_limits(self):
        """Check if provider is within rate limits"""
        from django.utils import timezone
        from datetime import timedelta

        # Check daily limit
        today = timezone.now().date()
        today_sent = EmailLog.objects.filter(
            smtp_provider=self,
            sent_at__date=today
        ).count()

        if today_sent >= self.emails_per_day:
            return False

        # Check hourly limit
        hour_ago = timezone.now() - timedelta(hours=1)
        hour_sent = EmailLog.objects.filter(
            smtp_provider=self,
            sent_at__gte=hour_ago
        ).count()

        return hour_sent < self.emails_per_hour


class EmailTemplate(models.Model):
    """Email template model for campaigns"""

    name = models.CharField(_('Template Name'), max_length=255, unique=True)
    subject = models.CharField(_('Email Subject'), max_length=500)
    html_content = RichTextUploadingField(_('HTML Content'))
    text_content = models.TextField(_('Text Content'), blank=True)
    is_active = models.BooleanField(_('Active'), default=True)

    # Template variables (JSON field for dynamic content)
    variables = models.JSONField(_('Template Variables'), default=dict, blank=True)

    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Email Template')
        verbose_name_plural = _('Email Templates')
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Campaign(models.Model):
    """Email campaign model"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(_('Campaign Name'), max_length=255)
    subject = models.CharField(_('Email Subject'), max_length=500)
    from_email = models.EmailField(_('From Email'))
    from_name = models.CharField(_('From Name'), max_length=255)
    reply_to_email = models.EmailField(_('Reply To'), blank=True)

    # Content
    html_content = RichTextUploadingField(_('HTML Content'), default='<p>Default campaign content</p>')
    text_content = models.TextField(_('Text Content'), blank=True)

    # Template reference
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)

    # Recipients
    subscriber_segments = models.ManyToManyField('subscribers.Segment', verbose_name=_('Subscriber Segments'), blank=True)

    # Settings
    smtp_provider = models.ForeignKey(SMTPProvider, on_delete=models.PROTECT, null=True, blank=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')

    # Scheduling

    sent_at = models.DateTimeField(_('Sent At'), null=True, blank=True)

    # Tracking
    total_recipients = models.IntegerField(_('Total Recipients'), default=0)
    total_sent = models.IntegerField(_('Total Sent'), default=0)
    total_delivered = models.IntegerField(_('Total Delivered'), default=0)
    total_opened = models.IntegerField(_('Total Opened'), default=0)
    total_clicked = models.IntegerField(_('Total Clicked'), default=0)
    total_bounced = models.IntegerField(_('Total Bounced'), default=0)
    total_unsubscribed = models.IntegerField(_('Total Unsubscribed'), default=0)

    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Campaign')
        verbose_name_plural = _('Campaigns')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_delivery_rate(self):
        """Calculate delivery rate percentage"""
        if self.total_sent == 0:
            return 0
        return (self.total_delivered / self.total_sent) * 100

    def get_open_rate(self):
        """Calculate open rate percentage"""
        if self.total_delivered == 0:
            return 0
        return (self.total_opened / self.total_delivered) * 100


class EmailLog(models.Model):
    """Email delivery log"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('bounced', 'Bounced'),
        ('failed', 'Failed'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, null=True, blank=True)
    subscriber_email = models.EmailField(_('Subscriber Email'))

    # SMTP Provider used
    smtp_provider = models.ForeignKey(SMTPProvider, on_delete=models.SET_NULL, null=True)

    # Email details
    subject = models.CharField(_('Subject'), max_length=500)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')

    # Tracking
    sent_at = models.DateTimeField(_('Sent At'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('Delivered At'), null=True, blank=True)
    opened_at = models.DateTimeField(_('Opened At'), null=True, blank=True)
    clicked_at = models.DateTimeField(_('Clicked At'), null=True, blank=True)
    bounced_at = models.DateTimeField(_('Bounced At'), null=True, blank=True)
    failed_at = models.DateTimeField(_('Failed At'), null=True, blank=True)

    # Error details
    error_message = models.TextField(_('Error Message'), blank=True)
    bounce_reason = models.TextField(_('Bounce Reason'), blank=True)

    # Tracking IDs
    message_id = models.CharField(_('Message ID'), max_length=255, blank=True)
    tracking_id = models.CharField(_('Tracking ID'), max_length=255, blank=True)

    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Email Log')
        verbose_name_plural = _('Email Logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['campaign', 'status']),
            models.Index(fields=['subscriber_email', 'status']),
            models.Index(fields=['smtp_provider', 'sent_at']),
        ]

    def __str__(self):
        return f"{self.subscriber_email} - {self.subject} ({self.status})"