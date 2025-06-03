from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal

# --- API Models ---
class PRReviewRequest(BaseModel):
    """
    Request model for the PR review API endpoint.
    """
    pr_url: str = Field(..., description="The full URL of the GitHub Pull Request (e.g., 'https://github.com/owner/repo/pull/123').")

class PRReviewResponse(BaseModel):
    """
    Response model for the PR review API endpoint, returning the final report.
    """
    report: Dict[str, Any] = Field(..., description="The comprehensive Pull Request Review Report in JSON format.")
    # You might want to define a specific Pydantic model for the report instead of Dict[str, Any]
    # For now, keeping it general, but ideally, this would be PullRequestReviewReport


# --- CrewAI Agent Output Models (Moved from main1.py) ---
class RepoContextAgentOutput(BaseModel):
    repo_purpose_summary: str = Field(description="A concise summary of the entire repository's main purpose and domain.")
    key_modules_concerns_goals: List[str] = Field(description="List of core modules, architectural concerns (e.g., performance, scalability, security), and main goals of the project derived from the README and file structure.")
    technologies_used: List[str] = Field(description="Identified major technologies, frameworks, and languages used in the repository (e.g., 'React', 'Node.js', 'Python', 'Flask', 'SQL').")
    common_patterns_conventions: List[str] = Field(description="Common coding patterns, architectural styles, or naming conventions observed (e.g., 'MVC pattern', 'RESTful APIs', 'CamelCase for variables', 'Redux for state management', 'PEP8 compliance').")
    pr_message_context_summary: str = Field(description="A summary of the committer's stated intent, the problem this PR aims to solve, and the high-level approach taken, extracted from the initial PR message.")


class BugFinding(BaseModel):
    file: str = Field(description="The name of the file where the bug is found.")
    line_numbers: List[int] = Field(description="A list of line numbers where the issue is located.")
    code_snippet: Optional[str] = Field(None, description="The exact code snippet where the bug is found.")
    description: str = Field(description="A clear description of the bug and why it's a problem.")
    severity: Literal["Critical", "High", "Medium", "Low"] = Field(description="The severity level of the bug.")
    suggested_fix: str = Field(description="A concrete and actionable suggestion to fix the bug.")

class BugDetectionAgentOutput(BaseModel):
    has_bugs: bool = Field(description="True if any bugs were detected, False otherwise.")
    findings: List[BugFinding] = Field(description="A list of detailed bug findings.")
    overall_assessment: Optional[str] = Field(None, description="An overall assessment of the bug risk for the pull request.")


class CodeQualitySuggestion(BaseModel):
    file: str = Field(description="The name of the file where the suggestion applies.")
    line_numbers: List[int] = Field(description="A list of line numbers relevant to the suggestion.")
    code_block: Optional[str] = Field(None, description="The code block relevant to the suggestion.")
    description: str = Field(description="A clear description of the code quality issue.")
    suggestion: str = Field(description="Actionable advice to improve code quality.")
    category: str = Field(description="Category of the suggestion (e.g., 'Readability', 'Maintainability', 'Performance', 'Best Practice').")

class CodeQualityAgentOutput(BaseModel):
    code_quality_score: int = Field(description="Overall code quality score (1-100).")
    suggestions: List[CodeQualitySuggestion] = Field(description="A list of detailed code quality suggestions.")
    summary_comment: str = Field(description="An overall summary comment on the code quality of the PR.")


class SecurityFinding(BaseModel):
    file: str = Field(description="The name of the file where the vulnerability is found.")
    line_numbers: List[int] = Field(description="A list of line numbers where the vulnerability is located.")
    code_snippet: Optional[str] = Field(None, description="The exact code snippet of the vulnerability.")
    title: str = Field(description="A short title for the security vulnerability (e.g., 'SQL Injection Vulnerability').")
    explanation: str = Field(description="Detailed explanation of the vulnerability and its potential impact.")
    risk_level: Literal["Critical", "High", "Medium", "Low", "Informational"] = Field(description="The risk level of the security vulnerability.")
    recommended_mitigation: str = Field(description="Concrete steps or recommendations to mitigate the vulnerability.")

class SecurityAgentOutput(BaseModel):
    has_security_vulnerabilities: bool = Field(description="True if any security vulnerabilities were detected, False otherwise.")
    findings: List[SecurityFinding] = Field(description="A list of detailed security findings.")
    overall_security_assessment: Optional[str] = Field(None, description="An overall assessment of the security posture of the pull request.")


class AlignmentAgentOutput(BaseModel):
    alignment_score: int = Field(description="A score (0-100) indicating how well the PR aligns with the repository's purpose and goals.")
    pr_nature_classification: Literal['Core Improvement', 'Feature Addition', 'Bug Fix', 'Refactoring', 'Documentation', 'Peripheral', 'Off-topic'] = Field(description="Classification of the PR's nature based on its stated purpose and changes.")
    justification: str = Field(description="A detailed explanation of why the PR aligns or deviates, referencing the repository context and PR message.")
    potential_misalignment_risks: List[str] = Field(description="Any long-term risks or architectural debt that could arise if this type of change is frequently introduced.")


class PullRequestReviewReport(BaseModel):
    overall_verdict: Literal["Approved", "Changes Requested", "Needs More Review"] = Field(description="The final recommendation for the pull request.")
    executive_summary: str = Field(description="A high-level summary of the PR's overall state, suitable for project managers or leads.")
    bug_risk_summary: str = Field(description="A summary of potential bugs and their risks.")
    code_quality_summary: str = Field(description="A summary of the code quality assessment.")
    security_summary: str = Field(description="A summary of identified security vulnerabilities.")
    alignment_summary: str = Field(description="A summary of how well the PR aligns with the project goals.")
    detailed_findings: Dict[str, Any] = Field(description="Includes the full Pydantic outputs from all sub-agents for completeness.")
    committer_feedback: str = Field(description="Human-like, empathetic, and constructive feedback for the committer.")
    actionable_next_steps_for_committer: List[str] = Field(description="A bulleted list of concrete, prioritized actions for the committer.")