from fastapi import FastAPI
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from routes import router as review_router # Import the router

load_dotenv() # Load environment variables at the application start

app = FastAPI(
    title="GitHub PR Reviewer AI",
    description="An AI-powered service to automate Pull Request reviews using CrewAI.",
    version="1.0.0"
)
origins = [
    "http://localhost:5173",
    # Add more origins here
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the GitHub PR Reviewer API! Visit /docs for API documentation."}