
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from mail.campaigns.models import SMTPProvider
import json

class Command(BaseCommand):
    help = 'Manages the warm-up schedule for SMTP providers.'

    def add_arguments(self, parser):
        parser.add_argument('provider_id', type=int, help='The ID of the SMTP provider to manage.')
        parser.add_argument('--start', action='store_true', help='Start the warm-up process.')
        parser.add_argument('--stop', action='store_true', help='Stop the warm-up process.')
        parser.add_argument('--schedule', type=str, help='A JSON string representing the warm-up schedule.')

    def handle(self, *args, **options):
        provider_id = options['provider_id']
        try:
            provider = SMTPProvider.objects.get(pk=provider_id)
        except SMTPProvider.DoesNotExist:
            raise CommandError(f'SMTP Provider with ID "{provider_id}" does not exist.')

        if options['start']:
            provider.is_warming_up = True
            provider.warmup_started_at = timezone.now()
            if options['schedule']:
                try:
                    provider.warmup_schedule = json.loads(options['schedule'])
                except json.JSONDecodeError:
                    raise CommandError('Invalid JSON format for schedule.')
            provider.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully started warm-up for provider "{provider.name}".'))

        elif options['stop']:
            provider.is_warming_up = False
            provider.warmup_started_at = None
            provider.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully stopped warm-up for provider "{provider.name}".'))

        elif options['schedule']:
            try:
                provider.warmup_schedule = json.loads(options['schedule'])
                provider.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully updated warm-up schedule for provider "{provider.name}".'))
            except json.JSONDecodeError:
                raise CommandError('Invalid JSON format for schedule.')
        else:
            self.stdout.write('No action specified. Use --start, --stop, or --schedule.')