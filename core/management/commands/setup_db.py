import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from pathlib import Path


class Command(BaseCommand):
    help = 'Set up the initial database with migrations and fixtures'
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Setting up the database...'))
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(settings.BASE_DIR, 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            self.stdout.write(self.style.SUCCESS('Created logs directory'))
        
        # Make migrations
        self.stdout.write(self.style.SUCCESS('Making migrations...'))
        call_command('makemigrations')
        
        # Apply migrations
        self.stdout.write(self.style.SUCCESS('Applying migrations...'))
        call_command('migrate')
        
        # Load fixtures
        self.stdout.write(self.style.SUCCESS('Loading initial data...'))
        
        # Load user fixtures
        users_fixture = os.path.join('users', 'fixtures', 'initial_users.json')
        if os.path.exists(os.path.join(settings.BASE_DIR, users_fixture)):
            call_command('loaddata', users_fixture)
            self.stdout.write(self.style.SUCCESS('Loaded initial users data'))
        else:
            self.stdout.write(self.style.WARNING(f'Fixture not found: {users_fixture}'))
        
        # Create static directory
        static_dir = os.path.join(settings.BASE_DIR, 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
            self.stdout.write(self.style.SUCCESS('Created static directory'))
        
        # Create media directory
        media_dir = os.path.join(settings.BASE_DIR, 'media')
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)
            self.stdout.write(self.style.SUCCESS('Created media directory'))
        
        # Collect static files
        self.stdout.write(self.style.SUCCESS('Collecting static files...'))
        call_command('collectstatic', '--noinput')
        
        self.stdout.write(self.style.SUCCESS('Database setup completed successfully!')) 