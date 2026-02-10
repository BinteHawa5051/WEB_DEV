import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to PostgreSQL server
connection = psycopg2.connect(
    host="localhost",
    port="5432",
    user="postgres",
    password="tooba@123"
)

connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = connection.cursor()

# Drop database if exists
print("Dropping database DEV_WEB...")
cursor.execute('DROP DATABASE IF EXISTS "DEV_WEB"')
print("✓ Database dropped")

# Create database
print("Creating database DEV_WEB...")
cursor.execute('CREATE DATABASE "DEV_WEB"')
print("✓ Database created")

cursor.close()
connection.close()

print("\n✓ Database recreated successfully!")
print("Now run: cd backend && alembic upgrade head")
