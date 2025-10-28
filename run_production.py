#!/usr/bin/env python
"""Production server runner with proper settings"""

import os
import sys
import subprocess

def run_production_server():
    """Run Django development server with production settings"""
    
    # Set the production settings module
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mail.settings_production'
    
    print(f"Using settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    
    # First test if we can import the settings
    try:
        from django.conf import settings
        print("✓ Django settings loaded successfully")
        print(f"✓ SECRET_KEY configured: {'***' if settings.SECRET_KEY else 'NOT SET'}")
        print(f"✓ DEBUG: {settings.DEBUG}")
        print(f"✓ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    except Exception as e:
        print(f"✗ Failed to load settings: {e}")
        return False
    
    # Run the server
    try:
        from django.core.management import execute_from_command_line
        print("Starting Django development server with production settings...")
        execute_from_command_line(['manage.py', 'runserver', '9988'])
    except Exception as e:
        print(f"✗ Failed to start server: {e}")
        return False

if __name__ == '__main__':
    run_production_server()