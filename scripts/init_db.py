import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database.database import engine, Base
from app.database.models import SearchHistory, Lead, SearchResult, MessageLog

def init_db():
    print("⏳ Connecting to Database...")
    try:
        # This one line does all the magic.
        # It looks at every class that inherits from 'Base' and creates the table.
        Base.metadata.create_all(bind=engine)
        print("✅ Success! Tables created in PostgreSQL.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    init_db()
