from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Sends a test email to a specified address using Django\'s console email backend for testing.'

    def add_arguments(self, parser):
        parser.add_argument('to_email', type=str, help='The email address to send the test email to.')
        parser.add_argument('--subject', type=str, default='Test Email', help='The subject of the test email.')
        parser.add_argument('--html_content', type=str, default='<h1>This is a test email.</h1>', help='The HTML content of the test email.')

    def handle(self, *args, **options):
        to_email = options['to_email']
        subject = options['subject']
        html_content = options['html_content']

        # Temporarily set to console backend for testing
        original_backend = settings.EMAIL_BACKEND
        settings.EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

        self.stdout.write(f"Attempting to send a test email to {to_email} using console backend...")

        try:
            send_mail(
                subject=subject,
                message=html_content,  # Plain text version
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=html_content,
            )
            self.stdout.write(self.style.SUCCESS(f"Test email would be sent to {to_email}. Check console output above."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to send email. Error: {str(e)}"))
        finally:
            # Restore original backend
            settings.EMAIL_BACKEND = original_backend
