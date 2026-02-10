from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uvicorn
from database import get_db, engine
from models import Base
from routers import auth, cases, judges, lawyers, scheduling, calendar, documents, ml_predictions, courts
import os
from dotenv import load_dotenv

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Courtroom Scheduling API",
    description="Intelligent court case scheduling system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(cases.router, prefix="/api/cases", tags=["Cases"])
app.include_router(judges.router, prefix="/api/judges", tags=["Judges"])
app.include_router(lawyers.router, prefix="/api/lawyers", tags=["Lawyers"])
app.include_router(scheduling.router, prefix="/api/scheduling", tags=["Scheduling"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(ml_predictions.router, prefix="/api/ml", tags=["ML Predictions"])
app.include_router(courts.router, prefix="/api/courts", tags=["Courts"])

@app.get("/")
async def root():
    return {"message": "Courtroom Scheduling API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)