import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time
from typing import Optional, Dict, Any
import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import requests
from django.utils import timezone

logger = logging.getLogger(__name__)


class SMTPService:
    """Comprehensive SMTP service for email delivery"""

    def __init__(self, provider):
        self.provider = provider
        self.connection = None

    def test_connection(self) -> Dict[str, Any]:
        """
        Test SMTP connection and authentication
        Returns: Dict with success status and message
        """
        try:
            if self.provider.provider_type in ['sendgrid', 'mailgun', 'ses', 'postmark']:
                return self._test_api_connection()
            else:
                return self._test_smtp_connection()
        except Exception as e:
            logger.error(f"Connection test failed for {self.provider.name}: {str(e)}")
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}'
            }

    def _test_smtp_connection(self) -> Dict[str, Any]:
        """Test traditional SMTP connection"""
        try:
            # Create SMTP connection
            if self.provider.use_ssl:
                server = smtplib.SMTP_SSL(self.provider.host, self.provider.port)
            else:
                server = smtplib.SMTP(self.provider.host, self.provider.port)
                if self.provider.use_tls:
                    server.starttls()

            # Test authentication
            if self.provider.username and self.provider.password:
                server.login(self.provider.username, self.provider.password)

            # Test sending capabilities
            server.noop()

            server.quit()

            return {
                'success': True,
                'message': 'SMTP connection successful'
            }

        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'message': 'Authentication failed. Check username and password.'
            }
        except smtplib.SMTPConnectError:
            return {
                'success': False,
                'message': 'Connection failed. Check host and port settings.'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection test failed: {str(e)}'
            }

    def _test_api_connection(self) -> Dict[str, Any]:
        """Test API-based email service connection"""
        try:
            if self.provider.provider_type == 'sendgrid':
                return self._test_sendgrid_connection()
            elif self.provider.provider_type == 'mailgun':
                return self._test_mailgun_connection()
            elif self.provider.provider_type == 'ses':
                return self._test_ses_connection()
            elif self.provider.provider_type == 'postmark':
                return self._test_postmark_connection()
            else:
                return {
                    'success': False,
                    'message': 'Unsupported API provider'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'API connection test failed: {str(e)}'
            }

    def _test_sendgrid_connection(self) -> Dict[str, Any]:
        """Test SendGrid API connection"""
        url = "https://api.sendgrid.com/v3/user/email"
        headers = {
            'Authorization': f'Bearer {self.provider.api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return {
                'success': True,
                'message': 'SendGrid API connection successful'
            }
        else:
            return {
                'success': False,
                'message': f'SendGrid API error: {response.status_code} - {response.text}'
            }

    def _test_mailgun_connection(self) -> Dict[str, Any]:
        """Test Mailgun API connection"""
        # Mailgun validation would go here
        return {
            'success': True,
            'message': 'Mailgun API connection test (implement based on Mailgun docs)'
        }

    def _test_ses_connection(self) -> Dict[str, Any]:
        """Test Amazon SES connection"""
        # SES validation would go here
        return {
            'success': True,
            'message': 'Amazon SES connection test (implement based on AWS SES docs)'
        }

    def _test_postmark_connection(self) -> Dict[str, Any]:
        """Test Postmark API connection"""
        url = "https://api.postmarkapp.com/sender"
        headers = {
            'X-Postmark-Server-Token': self.provider.api_key,
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return {
                'success': True,
                'message': 'Postmark API connection successful'
            }
        else:
            return {
                'success': False,
                'message': f'Postmark API error: {response.status_code} - {response.text}'
            }

    def send_email(self, to_email: str, subject: str, html_content: str,
                   text_content: str = None, attachments: list = None) -> Dict[str, Any]:
        """
        Send email using the configured provider
        Returns: Dict with success status and message_id or error
        """
        try:
            if self.provider.provider_type in ['sendgrid', 'mailgun', 'ses', 'postmark']:
                return self._send_via_api(to_email, subject, html_content, text_content, attachments)
            else:
                return self._send_via_smtp(to_email, subject, html_content, text_content, attachments)
        except Exception as e:
            logger.error(f"Email sending failed for {to_email}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _send_via_smtp(self, to_email: str, subject: str, html_content: str,
                       text_content: str = None, attachments: list = None) -> Dict[str, Any]:
        """Send email via traditional SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.provider.from_name} <{self.provider.from_email}>"
            msg['To'] = to_email

            if self.provider.reply_to_email:
                msg['Reply-To'] = self.provider.reply_to_email

            # Add content
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))

            # Add attachments
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)

            # Send email
            if self.provider.use_ssl:
                server = smtplib.SMTP_SSL(self.provider.host, self.provider.port)
            else:
                server = smtplib.SMTP(self.provider.host, self.provider.port)
                if self.provider.use_tls:
                    server.starttls()

            if self.provider.username and self.provider.password:
                server.login(self.provider.username, self.provider.password)

            # Send the email
            text = msg.as_string()
            server.sendmail(self.provider.from_email, to_email, text)
            server.quit()

            # Generate a message ID for tracking
            message_id = f"{int(time.time())}@{self.provider.host}"

            return {
                'success': True,
                'message_id': message_id
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _send_via_api(self, to_email: str, subject: str, html_content: str,
                      text_content: str = None, attachments: list = None) -> Dict[str, Any]:
        """Send email via API-based services"""
        if self.provider.provider_type == 'sendgrid':
            return self._send_sendgrid_email(to_email, subject, html_content, text_content)
        elif self.provider.provider_type == 'postmark':
            return self._send_postmark_email(to_email, subject, html_content, text_content)
        # Add other API providers as needed
        else:
            return {
                'success': False,
                'error': 'API provider not implemented'
            }

    def _send_sendgrid_email(self, to_email: str, subject: str, html_content: str,
                             text_content: str = None) -> Dict[str, Any]:
        """Send email via SendGrid API"""
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            'Authorization': f'Bearer {self.provider.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'personalizations': [{
                'to': [{'email': to_email}],
                'subject': subject
            }],
            'from': {
                'email': self.provider.from_email,
                'name': self.provider.from_name
            },
            'content': []
        }

        if text_content:
            data['content'].append({'type': 'text/plain', 'value': text_content})
        data['content'].append({'type': 'text/html', 'value': html_content})

        if self.provider.reply_to_email:
            data['reply_to'] = {'email': self.provider.reply_to_email}

        response = requests.post(url, headers=headers, json=data)

        if response.status_code in [200, 201, 202]:
            return {
                'success': True,
                'message_id': response.headers.get('X-Message-Id', 'sendgrid-' + str(int(time.time())))
            }
        else:
            return {
                'success': False,
                'error': f'SendGrid API error: {response.status_code} - {response.text}'
            }

    def _send_postmark_email(self, to_email: str, subject: str, html_content: str,
                             text_content: str = None) -> Dict[str, Any]:
        """Send email via Postmark API"""
        url = "https://api.postmarkapp.com/email"
        headers = {
            'X-Postmark-Server-Token': self.provider.api_key,
            'Content-Type': 'application/json'
        }

        data = {
            'From': f"{self.provider.from_name} <{self.provider.from_email}>",
            'To': to_email,
            'Subject': subject,
            'HtmlBody': html_content,
        }

        if text_content:
            data['TextBody'] = text_content

        if self.provider.reply_to_email:
            data['ReplyTo'] = self.provider.reply_to_email

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return {
                'success': True,
                'message_id': response.json().get('MessageID', 'postmark-' + str(int(time.time())))
            }
        else:
            return {
                'success': False,
                'error': f'Postmark API error: {response.status_code} - {response.text}'
            }

    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message"""
        filename = attachment.get('filename')
        content = attachment.get('content')
        mimetype = attachment.get('mimetype', 'application/octet-stream')

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(content)
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{filename}"'
        )
        part.add_header('Content-Type', mimetype)
        msg.attach(part)


class SMTPManager:
    """Manager for handling multiple SMTP providers and load balancing"""

    @staticmethod
    def get_active_providers():
        """Get all active SMTP providers"""
        from .models import SMTPProvider
        return SMTPProvider.objects.filter(is_active=True)

    @staticmethod
    def select_best_provider() -> Optional['SMTPProvider']:
        """
        Select the best available SMTP provider based on:
        1. Active status
        2. Rate limits
        3. Success rate
        4. Load balancing
        """
        from .models import SMTPProvider

        providers = SMTPProvider.objects.filter(is_active=True)

        if not providers:
            return None

        # Filter providers within rate limits
        available_providers = []
        for provider in providers:
            if provider.is_within_limits():
                available_providers.append(provider)

        if not available_providers:
            return None

        # Sort by success rate (delivery rate) and usage
        provider_scores = []
        for provider in available_providers:
            # Calculate score based on delivery rate and recent usage
            delivery_rate = provider.get_delivery_rate()
            # Prefer providers that haven't been used recently
            last_used_penalty = 0
            if provider.last_used:
                hours_since_used = (timezone.now() - provider.last_used).total_seconds() / 3600
                last_used_penalty = min(hours_since_used / 24, 1) * 10  # Max 10 point bonus

            score = delivery_rate + last_used_penalty
            provider_scores.append((provider, score))

        # Return provider with highest score
        provider_scores.sort(key=lambda x: x[1], reverse=True)
        return provider_scores[0][0]

    @staticmethod
    def test_all_providers() -> Dict[str, Any]:
        """Test all active SMTP providers"""
        providers = SMTPManager.get_active_providers()
        results = {}

        for provider in providers:
            service = SMTPService(provider)
            results[provider.name] = service.test_connection()

        return results

    @staticmethod
    def send_with_fallback(to_email: str, subject: str, html_content: str,
                          text_content: str = None, attachments: list = None) -> Dict[str, Any]:
        """
        Send email with automatic fallback to other providers if primary fails
        """
        providers = list(SMTPManager.get_active_providers())

        for provider in providers:
            service = SMTPService(provider)

            # Update last_used timestamp
            provider.last_used = timezone.now()
            provider.save(update_fields=['last_used'])

            result = service.send_email(to_email, subject, html_content, text_content, attachments)

            if result['success']:
                return result

        return {
            'success': False,
            'error': 'All SMTP providers failed'
        }