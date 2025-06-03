from fastapi import FastAPI, HTTPException
from controller import PostController
from models import RepoContextAgentOutput,BugFinding, BugDetectionAgentOutput, CodeQualitySuggestion, CodeQualityAgentOutput, SecurityFinding, SecurityAgentOutput, AlignmentAgentOutput, PullRequestReviewReport, LinkedInPostResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/Review-PR", response_model=LinkedInPostResponse)
def review_pr():):
    try
    