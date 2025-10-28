from django.core.management.base import BaseCommand
from campaigns.models import SMTPProvider

class Command(BaseCommand):
    help = 'Set up SMTP provider matching Listmonk configuration'

    def handle(self, *args, **options):
        # Check if provider already exists
        provider, created = SMTPProvider.objects.get_or_create(
            name='Listmonk SMTP',
            defaults={
                'provider_type': 'gmail',
                'is_active': True,
                'is_default': True,
                'host': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True,
                'use_ssl': False,
                'skip_tls_verify': False,
                'username': 'your-gmail@gmail.com',
                'password': '',  # User needs to set this in .env or admin
                'from_email': 'your-gmail@gmail.com',
                'from_name': 'Mail System',
                'emails_per_day': 1000,
                'emails_per_hour': 100,
                'emails_per_second': 2,
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created SMTP provider: {provider.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Provider {provider.name} already exists. Updating...')
            )
            # Update existing provider
            for attr, value in {
                'provider_type': 'gmail',
                'is_active': True,
                'is_default': True,
                'host': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True,
                'use_ssl': False,
                'skip_tls_verify': False,
                'username': 'your-gmail@gmail.com',
                'from_email': 'your-gmail@gmail.com',
                'from_name': 'Mail System',
                'emails_per_day': 1000,
                'emails_per_hour': 100,
                'emails_per_second': 2,
            }.items():
                setattr(provider, attr, value)
            provider.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated SMTP provider: {provider.name}')
            )

        self.stdout.write(
            self.style.SUCCESS('Please set the SMTP password in the admin interface or environment variables.')
        )