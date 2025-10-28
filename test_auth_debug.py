#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mail.settings')
django.setup()

from campaigns.models import SMTPProvider
from django.contrib.auth.models import User

def debug_smtp_test():
    print("=== SMTP Provider Debug ===")
    
    # Check if we have any users
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    if users.exists():
        print(f"First user: {users.first().username} (superuser: {users.first().is_superuser})")
    
    # Check SMTP providers
    providers = SMTPProvider.objects.filter(is_active=True)
    print(f"\nActive SMTP providers: {providers.count()}")
    
    for provider in providers:
        print(f"\n--- Provider ID: {provider.id} ---")
        print(f"Name: {provider.name}")
        print(f"Type: {provider.provider_type}")
        print(f"Host: {provider.host}:{provider.port}")
        print(f"Username: {provider.username}")
        print(f"From Email: {provider.from_email}")
        print(f"Password set: {'Yes' if provider.password else 'No'}")
        
        # Test connection
        try:
            from campaigns.smtp_service import SMTPService
            service = SMTPService(provider)
            result = service.test_connection()
            print(f"Test result: {result}")
        except Exception as e:
            print(f"Test error: {str(e)}")

if __name__ == "__main__":
    debug_smtp_test()