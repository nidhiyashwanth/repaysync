import os
import django
from django.db import connection

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "repaysync.settings")
django.setup()

def check_database():
    print("Checking database tables...")
    with connection.cursor() as cursor:
        # Get list of all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} tables in the database:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # Count rows in the table
            cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\"")
            count = cursor.fetchone()[0]
            print(f"    * Contains {count} rows")
            
            # Get column information
            cursor.execute(f"""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            # Check for specific tables of interest
            if table_name == 'users_user':
                print("    * Checking User model columns:")
                for col in columns:
                    col_name, data_type, max_length = col
                    print(f"      - {col_name}: {data_type}" + (f"({max_length})" if max_length else ""))
                
                # Check for missing columns
                column_names = [col[0] for col in columns]
                if 'created_at' not in column_names:
                    print("      ! WARNING: created_at column is missing")
                if 'updated_at' not in column_names:
                    print("      ! WARNING: updated_at column is missing")
                    
        # Check Django migrations table
        cursor.execute("""
            SELECT app, name, applied
            FROM django_migrations
            ORDER BY app, name
        """)
        migrations = cursor.fetchall()
        
        print("\nApplied migrations:")
        for app, name, applied in migrations:
            print(f"  {app}.{name} - Applied on {applied}")

if __name__ == "__main__":
    check_database() 