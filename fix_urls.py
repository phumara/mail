#!/usr/bin/env python3
"""
Fix Django URL references in templates to use direct paths instead of namespaced lookups
This bypasses the namespace caching issues temporarily
"""

import os
import re

def fix_template_urls():
    """Replace all problematic URL tags with direct paths"""

    # Define URL replacements
    replacements = {
        # Campaign URLs - from namespaced to direct paths
        r"\{% url 'campaigns:campaign_create' %\}": "/campaigns/create/",
        r"\{% url 'campaigns:campaign_list' %\}": "/campaigns/list/",
        r"\{% url 'campaigns:campaign_edit' campaign\.pk %\}": "/campaigns/campaign_edit/",
        r"\{% url 'campaigns:campaign_delete' campaign\.pk %\}": "/campaigns/campaign_delete/",
        r"\{% url 'campaigns:campaign_preview' campaign\.pk %\}": "/campaigns/campaign_preview/",
        r"\{% url 'campaigns:campaign_send' campaign\.pk %\}": "/campaigns/campaign_send/",
        r"\{% url 'campaigns:campaign_clone' campaign\.pk %\}": "/campaigns/campaign_clone/",
        r"\{% url 'campaigns:campaign_analytics' %\}": "/campaigns/analytics/",

        # Template URLs
        r"\{% url 'campaigns:template_create' %\}": "/campaigns/templates/create/",
        r"\{% url 'campaigns:template_list' %\}": "/campaigns/templates/",
        r"\{% url 'campaigns:template_edit' template\.pk %\}": "/campaigns/templates/template_edit/",
        r"\{% url 'campaigns:template_delete' template\.pk %\}": "/campaigns/templates/template_delete/",

        # SMTP URLs
        r"\{% url 'campaigns:smtp_manager' %\}": "/campaigns/smtp-manager/",
        r"\{% url 'campaigns:smtp_provider_create' %\}": "/campaigns/smtp-manager/create/",

        # Subscriber URLs (these are in subscribers namespace)
        r"\{% url 'subscribers:subscriber_list' %\}": "/subscribers/list/",
        r"\{% url 'subscribers:subscriber_import' %\}": "/subscribers/import/",
        r"\{% url 'subscribers:subscriber_bounces' %\}": "/subscribers/bounces/",
        r"\{% url 'subscribers:segment_list' %\}": "/subscribers/segments/",

        # Fix home URL reference
        r"\{% url 'campaigns:home' %\}": "/",

        # Fix main app home URL
        r"\{% url 'home' %\}": "/",
    }

    # Process all HTML template files
    mail_dir = "mail"
    total_fixes = 0

    for root, dirs, files in os.walk(mail_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)

                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_content = content
                for pattern, replacement in replacements.items():
                    content = re.sub(pattern, replacement, content)

                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    total_fixes += 1
                    print(f"Fixed: {filepath}")

    print(f"\nTotal files fixed: {total_fixes}")
    print("URL namespace issues temporarily resolved!")

if __name__ == "__main__":
    fix_template_urls()
