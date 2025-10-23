from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from .models import Campaign, EmailLog, SMTPProvider
from .smtp_service import SMTPService, SMTPManager
import logging
import time
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task
def send_campaign_email(campaign_id: int, subscriber_email: str, email_content: dict) -> dict:
    """
    Send a single campaign email to a subscriber
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id)

        # Get best available SMTP provider
        provider = SMTPManager.select_best_provider()

        if not provider:
            logger.error(f"No active SMTP providers available for campaign {campaign_id}")
            return {
                'success': False,
                'error': 'No SMTP providers available',
                'subscriber_email': subscriber_email
            }

        # Create email log entry
        email_log = EmailLog.objects.create(
            campaign=campaign,
            subscriber_email=subscriber_email,
            smtp_provider=provider,
            subject=email_content['subject'],
            status='pending'
        )

        # Send email using SMTP service
        service = SMTPService(provider)
        result = service.send_email(
            to_email=subscriber_email,
            subject=email_content['subject'],
            html_content=email_content['html_content'],
            text_content=email_content.get('text_content'),
            attachments=email_content.get('attachments', [])
        )

        # Update email log based on result
        with transaction.atomic():
            if result['success']:
                email_log.status = 'sent'
                email_log.sent_at = timezone.now()
                email_log.message_id = result.get('message_id', '')
                email_log.save()

                # Update campaign statistics
                campaign.total_sent += 1
                campaign.save(update_fields=['total_sent'])

                # Update provider statistics
                provider.total_sent += 1
                provider.save(update_fields=['total_sent'])

                logger.info(f"Email sent successfully to {subscriber_email} via {provider.name}")

                return {
                    'success': True,
                    'message_id': result.get('message_id'),
                    'subscriber_email': subscriber_email,
                    'provider': provider.name
                }
            else:
                email_log.status = 'failed'
                email_log.failed_at = timezone.now()
                email_log.error_message = result.get('error', 'Unknown error')
                email_log.save()

                logger.error(f"Failed to send email to {subscriber_email}: {result.get('error')}")

                return {
                    'success': False,
                    'error': result.get('error'),
                    'subscriber_email': subscriber_email
                }

    except Campaign.DoesNotExist:
        logger.error(f"Campaign {campaign_id} not found")
        return {
            'success': False,
            'error': 'Campaign not found',
            'subscriber_email': subscriber_email
        }
    except Exception as e:
        logger.error(f"Unexpected error sending email to {subscriber_email}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'subscriber_email': subscriber_email
        }


@shared_task
def send_bulk_campaign(campaign_id: int, batch_size: int = 50, delay: int = 1) -> dict:
    """
    Send campaign emails in batches with rate limiting
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id)

        if campaign.status not in ['scheduled', 'sending']:
            return {
                'success': False,
                'error': f'Campaign status is {campaign.status}, cannot send'
            }

        # Get subscribers who haven't received this campaign yet
        from subscribers.models import Subscriber

        sent_emails = EmailLog.objects.filter(
            campaign=campaign,
            status='sent'
        ).values_list('subscriber_email', flat=True)

        pending_subscribers = Subscriber.objects.exclude(
            email__in=sent_emails
        ).filter(
            is_active=True
        ).select_related()[:batch_size]

        if not pending_subscribers:
            # Mark campaign as sent if no more subscribers
            campaign.status = 'sent'
            campaign.sent_at = timezone.now()
            campaign.save()

            return {
                'success': True,
                'message': 'Campaign completed - no more subscribers',
                'emails_sent': 0
            }

        # Prepare email content
        email_content = {
            'subject': campaign.subject,
            'html_content': campaign.html_content,
            'text_content': campaign.text_content,
        }

        # Send emails to batch
        sent_count = 0
        failed_count = 0

        for subscriber in pending_subscribers:
            # Check rate limits before sending
            cache_key = f"smtp_rate_limit_{timezone.now().strftime('%Y%m%d%H%M')}"
            current_minute_sends = cache.get(cache_key, 0)

            if current_minute_sends >= 30:  # Max 30 emails per minute
                logger.info(f"Rate limit reached, pausing for {delay} seconds")
                time.sleep(delay)
                cache.set(cache_key, 0, 60)  # Reset counter

            # Send email asynchronously
            send_campaign_email.delay(campaign_id, subscriber.email, email_content)

            sent_count += 1
            cache.incr(cache_key)

            # Small delay between emails
            time.sleep(0.1)

        # Update campaign status if still sending
        if sent_count > 0:
            campaign.status = 'sending'
            campaign.save(update_fields=['status'])

        return {
            'success': True,
            'emails_sent': sent_count,
            'emails_failed': failed_count,
            'batch_size': batch_size
        }

    except Campaign.DoesNotExist:
        return {
            'success': False,
            'error': 'Campaign not found'
        }
    except Exception as e:
        logger.error(f"Error in bulk campaign sending: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def process_bounced_emails():
    """
    Process bounced emails and update subscriber status
    This would integrate with bounce handling services
    """
    # Placeholder for bounce processing logic
    # This would typically:
    # 1. Check bounce webhooks from email providers
    # 2. Parse bounce notifications
    # 3. Update EmailLog status
    # 4. Update subscriber status if too many bounces
    # 5. Update SMTP provider statistics

    logger.info("Processing bounced emails...")
    # Implementation would depend on the specific email provider APIs

    return {
        'success': True,
        'processed': 0
    }


@shared_task
def cleanup_old_email_logs(days: int = 90):
    """
    Clean up old email logs to save database space
    """
    from django.db import connection

    cutoff_date = timezone.now() - timezone.timedelta(days=days)

    deleted_count = EmailLog.objects.filter(
        created_at__lt=cutoff_date,
        status__in=['sent', 'delivered', 'bounced']
    ).delete()[0]

    logger.info(f"Cleaned up {deleted_count} old email logs")

    return {
        'success': True,
        'deleted_count': deleted_count
    }


@shared_task
def update_smtp_provider_stats():
    """
    Update SMTP provider statistics based on email logs
    """
    providers = SMTPProvider.objects.all()

    for provider in providers:
        logs = EmailLog.objects.filter(smtp_provider=provider)

        provider.total_sent = logs.count()
        provider.total_delivered = logs.filter(status='delivered').count()
        provider.total_bounced = logs.filter(status='bounced').count()
        provider.total_opened = logs.filter(status='opened').count()
        provider.total_clicked = logs.filter(status='clicked').count()

        provider.save(update_fields=[
            'total_sent', 'total_delivered', 'total_bounced',
            'total_opened', 'total_clicked'
        ])

    logger.info(f"Updated statistics for {len(providers)} SMTP providers")

    return {
        'success': True,
        'providers_updated': len(providers)
    }