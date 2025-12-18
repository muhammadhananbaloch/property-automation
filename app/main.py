from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import our modular routers
from app.api.routes import search, history

# Initialize the Application
app = FastAPI(
    title="Property Automation API",
    description="The backend engine for searching and enriching property leads.",
    version="2.0.0"
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

# --- REGISTER ROUTERS ---
# We plug in the "modules" we built
app.include_router(search.router)
app.include_router(history.router)

# --- ROOT ENDPOINT ---
# A simple health check to make sure the server is alive
@app.get("/")
def health_check():
    return {"status": "online", "message": "Property Automation API is running smoothly!"}
