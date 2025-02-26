from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routes import router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include Routes
app.include_router(router)

@app.get("/")
def home():
    return {"message": "FastAPI is running!"}
