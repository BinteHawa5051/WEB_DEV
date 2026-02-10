import psycopg2

# Connect to database
connection = psycopg2.connect(
    host="localhost",
    port="5432",
    user="postgres",
    password="tooba@123",
    database="DEV_WEB"
)

cursor = connection.cursor()

# Check current enum values
print("Checking current enum values...")
cursor.execute("""
    SELECT t.typname, e.enumlabel 
    FROM pg_type t 
    JOIN pg_enum e ON t.oid = e.enumtypid  
    WHERE t.typname IN ('userrole', 'courtlevel', 'jurisdiction', 'casestatus', 'urgencylevel')
    ORDER BY t.typname, e.enumsortorder;
""")

results = cursor.fetchall()
print("\nCurrent enum values in database:")
for row in results:
    print(f"  {row[0]}: {row[1]}")

print("\n" + "="*60)
print("The database has uppercase enum values (e.g., 'LAWYER')")
print("But our code expects lowercase values (e.g., 'lawyer')")
print("="*60)

cursor.close()
connection.close()

print("\nSolution: We need to drop and recreate the database with correct enum values.")
print("Run: python recreate_database.py")
print("Then: cd backend && alembic upgrade head")
