import os
from dotenv import load_dotenv
import psycopg2
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 1. Load the secrets
load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST", "127.0.0.1")
port = os.getenv("DB_PORT", "5432")
dbname = os.getenv("DB_NAME")

print("--- DEBUG INFO ---")
print(f"User:     '{user}'")
print(f"Password: '{password}'")
print(f"Host:     '{host}'")
print(f"Port:     '{port}'")
print(f"Database: '{dbname}'")
print("------------------")

print("\n(Attempting connection...)")
try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    print("✅ SUCCESS! Python connected to the database.")
    conn.close()
except Exception as e:
    print(f"❌ FAILURE: {e}")
