from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from models import PRReviewRequest, PRReviewResponse # Import request/response models
from controller import run_pr_review_crew # Import the core logic

router = APIRouter()

@router.post("/review-pr", response_model=PRReviewResponse)
async def review_pull_request(request: PRReviewRequest):
    """
    Receives a GitHub Pull Request URL and initiates an automated review process.
    Returns a comprehensive review report.
    """
    try:
        report = await run_pr_review_crew(request.pr_url)
        return PRReviewResponse(report=report)
    except HTTPException as e:
        raise e # Re-raise HTTPException for FastAPI to handle
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")