import os
import django
from django.db import connection

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "repaysync.settings")
django.setup()

# Fix User table if needed
with connection.cursor() as cursor:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users_user'")
    columns = [col[0] for col in cursor.fetchall()]
    
    # Add created_at and updated_at columns if they don't exist
    if 'created_at' not in columns:
        print("Adding created_at column...")
        cursor.execute("ALTER TABLE users_user ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()")
    
    if 'updated_at' not in columns:
        print("Adding updated_at column...")
        cursor.execute("ALTER TABLE users_user ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()")

# Now create the superuser
from django.contrib.auth import get_user_model

User = get_user_model()

# Check if superuser already exists
if not User.objects.filter(username='nidhiyashwanth').exists():
    # Create superuser
    user = User.objects.create_superuser(
        username='nidhiyashwanth',
        email='nidhiyashwanth007@gmail.com',
        password='supernidhi',
        first_name='Nidhi',
        last_name='Yashwanth',
        role='SUPER_MANAGER'
    )
    print(f"Superuser '{user.username}' created successfully.")
else:
    print("Superuser already exists.") 