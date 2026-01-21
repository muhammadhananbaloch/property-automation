from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, Base


# Import our modular routers
from app.api.routes import search, history, auth

from app.api.dependencies import get_current_user # <--- Import security dependency

# --- DATABASE INIT ---
# This automatically creates the 'users' table and any others that are missing.
# In a production environment, you would use Alembic for migrations instead.
Base.metadata.create_all(bind=engine)

# Initialize the Application
app = FastAPI(
    title="Property Automation API",
    description="The backend engine for searching and enriching property leads.",
    version="2.1.0"
)

# --- CORS SETTINGS ---
# This allows your future React Frontend (running on localhost:3000)
# to talk to this Python Backend (running on localhost:8000).
origins = [
    "http://localhost:3000",  # React default
    "http://localhost:5173",  # Vite default
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Auth Router (Public)
app.include_router(auth.router)

# 2. Protected Routers (Private)
app.include_router(
    search.router, 
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    history.router, 
    dependencies=[Depends(get_current_user)]
)

# --- ROOT ENDPOINT ---
# A simple health check to make sure the server is alive
@app.get("/")
def health_check():
    return {"status": "online", "message": "Property Automation API is running smoothly!"}
