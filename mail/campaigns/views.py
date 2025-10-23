from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import SMTPProvider, Campaign, EmailLog, EmailTemplate
from .forms import CampaignForm, TemplateForm
from .smtp_service import SMTPService, SMTPManager
import json
import traceback


@login_required
def smtp_dashboard(request):
    """Dashboard view for SMTP providers"""
    providers = SMTPProvider.objects.all()
    stats = []

    for provider in providers:
        service = SMTPService(provider)
        connection_test = service.test_connection()

        stats.append({
            'provider': provider,
            'connection_status': connection_test['success'],
            'connection_message': connection_test['message'],
            'delivery_rate': provider.get_delivery_rate(),
            'is_within_limits': provider.is_within_limits()
        })

    context = {
        'stats': stats,
        'total_providers': providers.count(),
        'active_providers': providers.filter(is_active=True).count(),
    }

    return render(request, 'campaigns/smtp_dashboard.html', context)


@login_required
@require_POST
def test_smtp_connection(request, provider_id):
    """AJAX view to test SMTP connection"""
    try:
        provider = get_object_or_404(SMTPProvider, id=provider_id)
        service = SMTPService(provider)
        result = service.test_connection()

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Test failed: {str(e)}'
        })


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
            return redirect('campaign_list')
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
            return redirect('campaign_list')
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
            return redirect('campaign_list')
    else:
        form = CampaignForm(instance=campaign)
    return render(request, 'campaigns/campaign_edit.html', {'form': form, 'campaign': campaign})


@login_required
def campaign_delete(request, pk):
    """Delete a campaign"""
    campaign = get_object_or_404(Campaign, pk=pk)
    if request.method == 'POST':
        campaign.delete()
        messages.success(request, f'Campaign "{campaign.name}" deleted successfully!')
        return redirect('campaign_list')
    return render(request, 'campaigns/campaign_delete.html', {'campaign': campaign})


@login_required
def media_list(request):
    """List media files"""
    return render(request, 'campaigns/media_list.html')


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
            template = form.save()
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