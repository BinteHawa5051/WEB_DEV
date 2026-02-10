import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import redis

# Load environment variables
load_dotenv('backend/.env')

def test_postgresql():
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        print(f"Testing PostgreSQL connection...")
        print(f"Database URL: {DATABASE_URL}")
        
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL connected successfully!")
            print(f"Version: {version}")
            return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_redis():
    try:
        REDIS_URL = os.getenv("REDIS_URL")
        print(f"\nTesting Redis connection...")
        print(f"Redis URL: {REDIS_URL}")
        
        r = redis.from_url(REDIS_URL)
        r.ping()
        print(f"✅ Redis connected successfully!")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Database Connections ===")
    
    pg_success = test_postgresql()
    redis_success = test_redis()
    
    print(f"\n=== Results ===")
    print(f"PostgreSQL: {'✅ Connected' if pg_success else '❌ Failed'}")
    print(f"Redis: {'✅ Connected' if redis_success else '❌ Failed'}")
    
    if pg_success and redis_success:
        print(f"\n🎉 All connections successful! Ready to start the application.")
    else:
        print(f"\n⚠️  Please fix the failed connections before proceeding.")