import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load environment variables
load_dotenv('backend/.env')

def create_database():
    try:
        # Connect to PostgreSQL server (not to a specific database)
        connection = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="tooba@123"
        )
        
        # Set autocommit mode
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create cursor
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'DEV_WEB'")
        exists = cursor.fetchone()
        
        if exists:
            print("✅ Database 'DEV_WEB' already exists!")
        else:
            # Create database
            cursor.execute('CREATE DATABASE "DEV_WEB"')
            print("✅ Database 'DEV_WEB' created successfully!")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False

if __name__ == "__main__":
    print("=== Creating PostgreSQL Database ===")
    success = create_database()
    
    if success:
        print("\n🎉 Database setup complete! Now testing connection...")
        
        # Test the connection
        os.system("python test_connection.py")
    else:
        print("\n⚠️  Database creation failed. Please check your PostgreSQL credentials.")