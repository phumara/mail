from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import SMTPProvider, Campaign, EmailLog, EmailTemplate
from .forms import CampaignForm, TemplateForm, SMTPProviderForm
from .smtp_service import SMTPService, SMTPManager
from subscribers.models import Subscriber
import json
import traceback
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Media
from .forms import MediaForm


@login_required
def smtp_manager(request):
    """View for managing SMTP providers with user-specific permissions"""
    # Users can only see their own SMTP providers
    providers = SMTPProvider.objects.filter(created_by=request.user)
    
    context = {
        'providers': providers,
    }

    return render(request, 'campaigns/smtp_manager.html', context)


@login_required
def smtp_provider_create(request):
    """Create a new SMTP provider"""
    if request.method == 'POST':
        form = SMTPProviderForm(request.POST)
        if form.is_valid():
            provider = form.save(commit=False)
            provider.created_by = request.user
            provider.save()
            messages.success(request, 'SMTP Provider created successfully!')
            return redirect('campaigns:smtp_manager')
    else:
        form = SMTPProviderForm()
    return render(request, 'campaigns/smtp_provider_form.html', {'form': form, 'title': 'Create SMTP Provider'})


@login_required
def smtp_provider_edit(request, pk):
    """Edit an existing SMTP provider"""
    provider = get_object_or_404(SMTPProvider, pk=pk)
    
    # Check if user has permission to edit this provider
    if provider.created_by != request.user:
        messages.error(request, 'You don\'t have permission to edit this SMTP provider.')
        return redirect('campaigns:smtp_manager')
    
    if request.method == 'POST':
        form = SMTPProviderForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            messages.success(request, 'SMTP Provider updated successfully!')
            return redirect('campaigns:smtp_manager')
    else:
        form = SMTPProviderForm(instance=provider)
    return render(request, 'campaigns/smtp_provider_form.html', {'form': form, 'title': 'Edit SMTP Provider'})


@login_required
def smtp_provider_delete(request, pk):
    """Delete an SMTP provider"""
    provider = get_object_or_404(SMTPProvider, pk=pk)
    
    # Check if user has permission to delete this provider
    if provider.created_by != request.user:
        messages.error(request, 'You don\'t have permission to delete this SMTP provider.')
        return redirect('campaigns:smtp_manager')
    
    if request.method == 'POST':
        provider.delete()
        messages.success(request, 'SMTP Provider deleted successfully!')
        return redirect('campaigns:smtp_manager')
    return render(request, 'campaigns/smtp_provider_confirm_delete.html', {'provider': provider})


@login_required
@require_POST
def test_smtp_connection(request, provider_id):
    """AJAX view to test SMTP connection"""
    try:
        provider = get_object_or_404(SMTPProvider, id=provider_id)
        
        # Check if user has permission to test this provider
        if provider.created_by != request.user:
            return JsonResponse({
                'success': False,
                'message': 'You don\'t have permission to test this SMTP provider.'
            })
        
        service = SMTPService(provider)
        result = service.test_connection()

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Test failed: {str(e)}'
        })


@login_required
def send_test_email(request):
    """View to send a test email"""
    error = None
    to_email = ''
    if request.method == 'POST':
        to_email = request.POST.get('to_email')
        if not to_email:
            error = 'Please fill out this field.'
        else:
            # Get default SMTP provider
            default_provider = SMTPProvider.objects.filter(is_default=True, is_active=True).first()
            if not default_provider:
                messages.error(request, 'No default SMTP provider set.')
            else:
                # Send test email
                service = SMTPService(default_provider)
                result = service.send_email(
                    to_email=to_email,
                    subject='Test Email',
                    html_content='<p>This is a test email from your mail system.</p>',
                    text_content='This is a test email from your mail system.'
                )
        
                if result['success']:
                    messages.success(request, 'Test email sent successfully!')
                else:
                    messages.error(request, f'Failed to send test email: {result.get("error", "Unknown error")}')

    # For GET or after POST, show the form
    default_provider = SMTPProvider.objects.filter(is_default=True, is_active=True).first()
    if default_provider:
        from_email_display = f"{default_provider.from_name} <{default_provider.from_email}>"
    else:
        from_email_display = 'No default provider set'

    return render(request, 'campaigns/send_test_email.html', {'from_email': from_email_display, 'to_email': to_email, 'error': error})


@login_required
def campaign_analytics(request, campaign_id=None):
    """Campaign analytics view"""
    if campaign_id:
        campaign = get_object_or_404(Campaign, id=campaign_id)
        campaigns = [campaign]
    else:
        campaigns = Campaign.objects.all()

    # Calculate analytics
    analytics = []
    for campaign in campaigns:
        total_logs = EmailLog.objects.filter(campaign=campaign).count()

        analytics.append({
            'campaign': campaign,
            'total_logs': total_logs,
            'sent': EmailLog.objects.filter(campaign=campaign, status='sent').count(),
            'delivered': EmailLog.objects.filter(campaign=campaign, status='delivered').count(),
            'opened': EmailLog.objects.filter(campaign=campaign, status='opened').count(),
            'clicked': EmailLog.objects.filter(campaign=campaign, status='clicked').count(),
            'bounced': EmailLog.objects.filter(campaign=campaign, status='bounced').count(),
            'failed': EmailLog.objects.filter(campaign=campaign, status='failed').count(),
            'delivery_rate': campaign.get_delivery_rate(),
            'open_rate': campaign.get_open_rate(),
        })

    context = {
        'analytics': analytics,
        'selected_campaign': campaign_id,
    }

    return render(request, 'campaigns/analytics.html', context)


@login_required
def email_logs(request):
    """View email delivery logs"""
    logs = EmailLog.objects.select_related('campaign', 'smtp_provider').order_by('-created_at')

    # Filter options
    status_filter = request.GET.get('status')
    provider_filter = request.GET.get('provider')
    campaign_filter = request.GET.get('campaign')

    if status_filter:
        logs = logs.filter(status=status_filter)

    if provider_filter:
        logs = logs.filter(smtp_provider_id=provider_filter)

    if campaign_filter:
        logs = logs.filter(campaign_id=campaign_filter)

    # Pagination (simple implementation)
    page = int(request.GET.get('page', 1))
    per_page = 50
    start = (page - 1) * per_page
    end = start + per_page

    logs_page = logs[start:end]

    context = {
        'logs': logs_page,
        'total_logs': logs.count(),
        'current_page': page,
        'total_pages': (logs.count() + per_page - 1) // per_page,
        'status_choices': EmailLog.STATUS_CHOICES,
        'providers': SMTPProvider.objects.filter(is_active=True),
        'campaigns': Campaign.objects.all(),
        'current_filters': {
            'status': status_filter,
            'provider': provider_filter,
            'campaign': campaign_filter,
        }
    }

    return render(request, 'campaigns/email_logs.html', context)


@login_required
def campaign_list(request):
    """List all campaigns"""
    campaigns = Campaign.objects.all().order_by('-created_at')
    return render(request, 'campaigns/campaign_list.html', {'campaigns': campaigns})


@login_required
def campaign_create(request):
    """Create a new campaign"""
    if request.method == 'POST':
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save()
            messages.success(request, f'Campaign "{campaign.name}" created successfully!')
            return redirect('campaigns:campaign_list')
    else:
        form = CampaignForm()
    return render(request, 'campaigns/campaign_create.html', {'form': form})


@login_required
def campaign_create_simple(request):
    """Create a simple campaign"""
    if request.method == 'POST':
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save()
            messages.success(request, f'Campaign "{campaign.name}" created successfully!')
            return redirect('campaigns:campaign_list')
    else:
        form = CampaignForm()
    return render(request, 'campaigns/campaign_create_simple.html', {'form': form})


@login_required
def campaign_edit(request, pk):
    """Edit a campaign"""
    campaign = get_object_or_404(Campaign, pk=pk)
    if request.method == 'POST':
        form = CampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            messages.success(request, f'Campaign "{campaign.name}" updated successfully!')
            return redirect('campaigns:campaign_list')
    else:
        form = CampaignForm(instance=campaign)
    return render(request, 'campaigns/edit.html', {'form': form, 'campaign': campaign})


@login_required
def campaign_delete(request, pk):
    """Delete a campaign"""
    campaign = get_object_or_404(Campaign, pk=pk)
    if request.method == 'POST':
        campaign.delete()
        messages.success(request, f'Campaign "{campaign.name}" deleted successfully!')
        return redirect('campaigns:campaign_list')
    return render(request, 'campaigns/campaign_delete.html', {'campaign': campaign})


@login_required
def campaign_preview(request, pk):
    """Preview a campaign's HTML content"""
    campaign = get_object_or_404(Campaign, pk=pk)
    return render(request, 'campaigns/campaign_preview.html', {'campaign': campaign})


@login_required
def campaign_clone(request, pk):
    """Clone an existing campaign"""
    original_campaign = get_object_or_404(Campaign, pk=pk)
    
    # Create a new campaign object by copying values
    new_campaign = Campaign(
        name=f'{original_campaign.name} (Clone)',
        subject=original_campaign.subject,
        from_email=original_campaign.from_email,
        from_name=original_campaign.from_name,
        reply_to_email=original_campaign.reply_to_email,
        html_content=original_campaign.html_content,
        text_content=original_campaign.text_content,
        template=original_campaign.template,
        smtp_provider=original_campaign.smtp_provider,
        status='draft', # Cloned campaigns start as drafts
        created_by=request.user # Assign current user as creator
    )
    new_campaign.save()

    # Copy ManyToMany relationships (subscriber_segments)
    new_campaign.subscriber_segments.set(original_campaign.subscriber_segments.all())

    messages.success(request, f'Campaign "{new_campaign.name}" cloned successfully!')
    return redirect('campaigns:campaign_edit', pk=new_campaign.pk)


@login_required
def campaign_send(request, pk):
    """Send a campaign to selected segments"""
    campaign = get_object_or_404(Campaign, pk=pk)

    if campaign.status != 'draft':
        messages.error(request, f'Campaign "{campaign.name}" cannot be sent as it is not in draft status.')
        return redirect('campaigns:campaign_list')

    if not campaign.subscriber_segments.exists():
        messages.error(request, f'Campaign "{campaign.name}" has no target segments selected.')
        return redirect('campaigns:campaign_edit', pk=campaign.pk)

    if not campaign.smtp_provider:
        default_provider = SMTPProvider.objects.filter(is_default=True, is_active=True).first()
        if default_provider:
            campaign.smtp_provider = default_provider
            campaign.save() # Save the campaign with the default provider
        else:
            messages.error(request, f'Campaign "{campaign.name}" has no SMTP provider selected and no default active provider is set.')
            return redirect('campaigns:campaign_edit', pk=campaign.pk)

    # Update campaign status to sending
    campaign.status = 'sending'
    campaign.save()

    total_sent_count = 0
    smtp_service = SMTPService(campaign.smtp_provider)

    # Get all unique subscribers from the selected segments
    subscribers_to_send = Subscriber.objects.filter(segments__in=campaign.subscriber_segments.all()).distinct()

    for subscriber in subscribers_to_send:
        try:
            # Replace placeholders in subject and content
            subject = campaign.subject.replace('{subscriber.name}', subscriber.name or '').replace('{subscriber.email}', subscriber.email)
            html_content = campaign.html_content.replace('{subscriber.name}', subscriber.name or '').replace('{subscriber.email}', subscriber.email)
            text_content = campaign.text_content.replace('{subscriber.name}', subscriber.name or '').replace('{subscriber.email}', subscriber.email)

            success = smtp_service.send_email(
                to_email=subscriber.email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
            )

            if success:
                total_sent_count += 1
                EmailLog.objects.create(
                    campaign=campaign,
                    subscriber_email=subscriber.email,
                    smtp_provider=campaign.smtp_provider,
                    subject=subject,
                    status='sent',
                    sent_at=timezone.now()
                )
            else:
                EmailLog.objects.create(
                    campaign=campaign,
                    subscriber_email=subscriber.email,
                    smtp_provider=campaign.smtp_provider,
                    subject=subject,
                    status='failed',
                    error_message='SMTP service failed to send email.',
                    sent_at=timezone.now()
                )
        except Exception as e:
            EmailLog.objects.create(
                campaign=campaign,
                subscriber_email=subscriber.email,
                smtp_provider=campaign.smtp_provider,
                subject=campaign.subject,
                status='failed',
                error_message=f'Error sending email: {str(e)}',
                sent_at=timezone.now()
            )
            messages.error(request, f'Error sending email to {subscriber.email}: {str(e)}')

    # Update campaign status and sent count after sending attempts
    campaign.total_recipients = subscribers_to_send.count()
    campaign.total_sent = total_sent_count
    campaign.status = 'sent'
    campaign.sent_at = timezone.now()
    campaign.save()

    messages.success(request, f'Campaign "{campaign.name}" sent to {total_sent_count} recipients.')
    return redirect('campaigns:campaign_list')


@login_required
def template_list(request):
    """List all templates"""
    templates = EmailTemplate.objects.all().order_by('-created_at')
    return render(request, 'campaigns/template_list.html', {'templates': templates})


@login_required
def template_create(request):
    """Create a new template"""
    if request.method == 'POST':
        form = TemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()
            messages.success(request, f'Template "{template.name}" created successfully!')
            return redirect('campaigns:template_list')
    else:
        form = TemplateForm()
    return render(request, 'campaigns/template_create.html', {'form': form})


@login_required
def template_edit(request, pk):
    """Edit a template"""
    template = get_object_or_404(EmailTemplate, pk=pk)
    if request.method == 'POST':
        form = TemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, f'Template "{template.name}" updated successfully!')
            return redirect('campaigns:template_list')
    else:
        form = TemplateForm(instance=template)
    return render(request, 'campaigns/template_edit.html', {'form': form, 'template': template})


@login_required
def template_delete(request, pk):
    """Delete a template"""
    template = get_object_or_404(EmailTemplate, pk=pk)
    if request.method == 'POST':
        template.delete()
        messages.success(request, f'Template "{template.name}" deleted successfully!')
        return redirect('campaigns:template_list')
    return render(request, 'campaigns/template_delete.html', {'template': template})


@login_required
def smtp_settings(request):
    """Redirects to the SMTPProvider admin page."""
    return redirect('/admin/campaigns/smtpprovider/')

class MediaListView(View):
    """View to display a list of media files"""
    def get(self, request):
        media_files = Media.objects.all()
        return render(request, 'campaigns/media_list.html', {'media_files': media_files})


class MediaUploadView(View):
    """View to handle media file uploads"""
    def get(self, request):
        form = MediaForm()
        return render(request, 'campaigns/media_upload.html', {'form': form})

    def post(self, request):
        form = MediaForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save(commit=False)
            media.uploaded_by = request.user
            media.save()
            return redirect('campaigns:media_list')
        return render(request, 'campaigns/media_upload.html', {'form': form})


class MediaDeleteView(View):
    """View to delete a media file"""
    def post(self, request, pk):
        media = get_object_or_404(Media, pk=pk)
        media.delete()
        return redirect('campaigns:media_list')