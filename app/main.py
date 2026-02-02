from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, Base

# Import our modular routers
# Added 'webhooks' to the list
from app.api.routes import search, history, auth, campaigns, messages, webhooks

from app.api.dependencies import get_current_user # <--- Import security dependency

# --- DATABASE INIT ---
Base.metadata.create_all(bind=engine)

# Initialize the Application
app = FastAPI(
    title="Property Automation API",
    description="The backend engine for searching and enriching property leads.",
    version="2.1.0"
)

# --- CORS SETTINGS ---
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

# 2. Webhooks Router (Public - Secured by Twilio Signature)
# We do NOT add get_current_user dependency here because Twilio is not a user.
app.include_router(webhooks.router)

# 3. Protected Routers (Private)
app.include_router(
    search.router, 
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    history.router, 
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    campaigns.router,
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    messages.router,
    dependencies=[Depends(get_current_user)]
)

# --- ROOT ENDPOINT ---
@app.get("/")
def health_check():
    return {"status": "online", "message": "Property Automation API is running smoothly!"}