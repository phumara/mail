from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.html import format_html
from django.utils import timezone
from .models import SMTPProvider, EmailTemplate, Campaign, EmailLog
from .smtp_service import SMTPService, SMTPManager


@admin.register(SMTPProvider)
class SMTPProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider_type', 'is_active', 'is_default', 'delivery_rate', 'total_sent', 'last_used', 'test_connection_button']
    list_filter = ['provider_type', 'is_active', 'is_default', 'created_at']
    search_fields = ['name', 'host', 'from_email']
    readonly_fields = ['total_sent', 'total_delivered', 'total_bounced', 'total_opened', 'total_clicked', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'provider_type', 'is_active', 'is_default')
        }),
        ('SMTP Settings', {
            'fields': ('host', 'port', 'use_tls', 'use_ssl')
        }),
        ('Authentication', {
            'fields': ('username', 'password'),
            'classes': ('collapse',)
        }),
        ('API Settings (for API-based providers)', {
            'fields': ('api_key', 'api_secret'),
            'classes': ('collapse',)
        }),
        ('Email Settings', {
            'fields': ('from_email', 'from_name', 'reply_to_email')
        }),
        ('Rate Limits', {
            'fields': ('emails_per_day', 'emails_per_hour', 'emails_per_second'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_sent', 'total_delivered', 'total_bounced', 'total_opened', 'total_clicked', 'last_used'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def test_connection_button(self, obj):
        """Display test connection button"""
        return format_html(
            '<a class="button" href="{}" target="_blank">Test Connection</a>',
            f'/admin/campaigns/smtpprovider/{obj.id}/test-connection/'
        )
    test_connection_button.short_description = 'Test'

    def delivery_rate(self, obj):
        """Display delivery rate percentage"""
        rate = obj.get_delivery_rate()
        color = 'green' if rate > 90 else 'orange' if rate > 70 else 'red'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, rate)
    delivery_rate.short_description = 'Delivery Rate'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:provider_id>/test-connection/',
                self.admin_site.admin_view(self.test_connection_view),
                name='test_smtp_connection',
            ),
        ]
        return custom_urls + urls

    def test_connection_view(self, request, provider_id):
        """View to test SMTP connection"""
        try:
            provider = self.model.objects.get(pk=provider_id)
            service = SMTPService(provider)
            result = service.test_connection()

            if result['success']:
                messages.success(request, f"✅ {result['message']}")
            else:
                messages.error(request, f"❌ {result['message']}")

        except self.model.DoesNotExist:
            messages.error(request, "SMTP Provider not found")
        except Exception as e:
            messages.error(request, f"Test failed: {str(e)}")

        return HttpResponseRedirect(f'/admin/campaigns/smtpprovider/{provider_id}/change/')

    def save_model(self, request, obj, form, change):
        """Test connection when saving if it's a new provider"""
        super().save_model(request, obj, form, change)

        if not change:  # New provider
            service = SMTPService(obj)
            result = service.test_connection()
            if result['success']:
                messages.success(request, f"✅ Connection successful for {obj.name}")
            else:
                messages.warning(request, f"⚠️ {obj.name}: {result['message']}")


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'subject']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'subject', 'is_active')
        }),
        ('Content', {
            'fields': ('html_content', 'text_content')
        }),
        ('Template Variables', {
            'fields': ('variables',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'smtp_provider', 'total_recipients', 'total_sent', 'delivery_rate', 'created_at']
    list_filter = ['status', 'smtp_provider', 'created_at']
    search_fields = ['name', 'subject']
    readonly_fields = ['total_sent', 'total_delivered', 'total_opened', 'total_clicked', 'total_bounced', 'total_unsubscribed', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'subject', 'status')
        }),
        ('Email Settings', {
            'fields': ('from_email', 'from_name', 'reply_to_email')
        }),
        ('Content', {
            'fields': ('html_content', 'text_content', 'template')
        }),
        ('Recipients', {
            'fields': ('subscriber_lists',)
        }),
        ('SMTP Provider', {
            'fields': ('smtp_provider',)
        }),

        ('Statistics', {
            'fields': ('total_recipients', 'total_sent', 'total_delivered', 'total_opened', 'total_clicked', 'total_bounced', 'total_unsubscribed'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def delivery_rate(self, obj):
        """Display delivery rate percentage"""
        rate = obj.get_delivery_rate()
        color = 'green' if rate > 90 else 'orange' if rate > 70 else 'red'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, rate)
    delivery_rate.short_description = 'Delivery Rate'


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['subscriber_email', 'campaign', 'smtp_provider', 'status', 'sent_at', 'created_at']
    list_filter = ['status', 'smtp_provider', 'sent_at', 'created_at']
    search_fields = ['subscriber_email', 'subject', 'message_id']
    readonly_fields = ['created_at', 'updated_at', 'sent_at', 'delivered_at', 'opened_at', 'clicked_at', 'bounced_at', 'failed_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('campaign', 'subscriber_email', 'subject', 'status')
        }),
        ('SMTP Provider', {
            'fields': ('smtp_provider',)
        }),
        ('Timestamps', {
            'fields': ('sent_at', 'delivered_at', 'opened_at', 'clicked_at', 'bounced_at', 'failed_at')
        }),
        ('Error Details', {
            'fields': ('error_message', 'bounce_reason'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('message_id', 'tracking_id'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Disable adding email logs manually"""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable changing email logs"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deleting email logs"""
        return False