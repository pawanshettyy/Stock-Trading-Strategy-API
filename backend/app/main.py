from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router  # Ensure this import works
import logging

app = FastAPI(title="Stock Trading Strategy API")

# Enable detailed error logs
logging.basicConfig(level=logging.DEBUG)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes (Ensure router is imported correctly)
app.include_router(router)

@app.get("/")
def home():
    return {"message": "Stock Trading Strategy API is running!"}
