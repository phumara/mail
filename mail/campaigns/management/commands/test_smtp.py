from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from campaigns.models import SMTPProvider
from campaigns.smtp_service import SMTPService, SMTPManager
import json


class Command(BaseCommand):
    help = 'Test SMTP connections for all active providers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--provider',
            type=str,
            help='Test specific provider by name',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Test all providers (including inactive)',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output results in JSON format',
        )

    def handle(self, *args, **options):
        provider_name = options.get('provider')
        test_all = options.get('all')
        json_output = options.get('json')

        if provider_name:
            # Test specific provider
            try:
                if test_all:
                    provider = SMTPProvider.objects.get(name=provider_name)
                else:
                    provider = SMTPProvider.objects.get(name=provider_name, is_active=True)

                service = SMTPService(provider)
                result = service.test_connection()

                if json_output:
                    self.stdout.write(json.dumps({
                        'provider': provider.name,
                        'result': result
                    }, indent=2))
                else:
                    if result['success']:
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ {provider.name}: {result['message']}")
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"❌ {provider.name}: {result['message']}")
                        )

            except SMTPProvider.DoesNotExist:
                raise CommandError(f"Provider '{provider_name}' not found")

        else:
            # Test all providers
            if test_all:
                providers = SMTPProvider.objects.all()
            else:
                providers = SMTPProvider.objects.filter(is_active=True)

            if not providers:
                if json_output:
                    self.stdout.write(json.dumps({'results': []}, indent=2))
                else:
                    self.stdout.write(self.style.WARNING('No SMTP providers found'))
                return

            results = {}

            for provider in providers:
                service = SMTPService(provider)
                result = service.test_connection()
                results[provider.name] = result

                if not json_output:
                    if result['success']:
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ {provider.name}: {result['message']}")
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"❌ {provider.name}: {result['message']}")
                        )

            if json_output:
                self.stdout.write(json.dumps({'results': results}, indent=2))

            # Summary
            if not json_output:
                successful = sum(1 for r in results.values() if r['success'])
                total = len(results)
                self.stdout.write(
                    self.style.SUCCESS(f"\nSummary: {successful}/{total} providers working")
                )