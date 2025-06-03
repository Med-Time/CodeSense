from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel, Field

from models import PRReviewRequest # Import request/response models
from controller import run_pr_review_crew # Import the core logic

router = APIRouter()

class PRReviewResponse(BaseModel):
    """
    Response model for the PR review API endpoint, returning the final report.
    """
    report: str = Field(..., description="The comprehensive Pull Request Review Report in Markdown format.")

@router.post("/review-pr", response_model=PRReviewResponse)
async def review_pull_request(request: PRReviewRequest) -> Dict[str, str]:
    """
    Reviews a GitHub Pull Request and returns a comprehensive analysis report in markdown format.
    """
    try:
        result = await run_pr_review_crew(request.pr_url)
        if isinstance(result, dict) and "report" in result:
            return result  # Already in {"report": "markdown"} format
        else:
            # If it's not in the expected format, wrap it
            return {"report": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reviewing PR: {str(e)}")