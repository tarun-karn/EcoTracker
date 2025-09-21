from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os


class Command(BaseCommand):
    help = 'Set up Google OAuth2 social application for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=str,
            help='Google OAuth2 Client ID',
            default='your-development-google-client-id.apps.googleusercontent.com'
        )
        parser.add_argument(
            '--client-secret', 
            type=str,
            help='Google OAuth2 Client Secret',
            default='your-development-google-client-secret'
        )

    def handle(self, *args, **options):
        client_id = options['client_id']
        client_secret = options['client_secret']
        
        # Ensure we have a Site object
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={
                'domain': '127.0.0.1:8000',
                'name': 'EcoTracker Development'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created site: {site.name} ({site.domain})')
            )
        
        # Create or update the Google social application
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth2',
                'client_id': client_id,
                'secret': client_secret,
            }
        )
        
        if not created:
            # Update existing app
            google_app.client_id = client_id
            google_app.secret = client_secret
            google_app.save()
            self.stdout.write(
                self.style.SUCCESS('Updated existing Google OAuth2 application')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Created new Google OAuth2 application')
            )
        
        # Add the site to the social app
        google_app.sites.add(site)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nGoogle OAuth2 setup complete!'
                f'\nClient ID: {client_id}'
                f'\nRedirect URI: http://127.0.0.1:8000/accounts/google/login/callback/'
                f'\n\nTo complete setup:'
                f'\n1. Go to https://console.developers.google.com/'
                f'\n2. Create a new project or select existing'
                f'\n3. Enable Google+ API (or Google Identity)'
                f'\n4. Create OAuth 2.0 credentials'
                f'\n5. Add http://127.0.0.1:8000/accounts/google/login/callback/ to authorized redirect URIs'
                f'\n6. Run this command again with your real credentials:'
                f'\n   python manage.py setup_google_oauth --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET'
            )
        )
        
        if client_id.startswith('your-development'):
            self.stdout.write(
                self.style.WARNING(
                    '\nWARNING: Using placeholder credentials! '
                    'Google OAuth2 will not work until you provide real credentials.'
                )
            )