from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Any, Optional, Literal

class RepoContextAgentOutput(BaseModel):
    repo_purpose_summary: str = Field(description="A concise summary of the entire repository's main purpose and domain.")
    key_modules_concerns_goals: List[str] = Field(description="List of core modules, architectural concerns (e.g., performance, scalability, security), and main goals of the project derived from the README and file structure.")
    technologies_used: List[str] = Field(description="Identified major technologies, frameworks, and languages used in the repository (e.g., 'React', 'Node.js', 'Python', 'Flask', 'SQL').")
    common_patterns_conventions: List[str] = Field(description="Common coding patterns, architectural styles, or naming conventions observed (e.g., 'MVC pattern', 'RESTful APIs', 'CamelCase for variables', 'Redux for state management').")
    pr_message_context_summary: str = Field(description="A summary of the pull request's initial message, highlighting the committer's stated intent, problem being solved, and proposed solution.")

class BugFinding(BaseModel):
    file: str = Field(description="The file path where the potential bug was found.")
    line_numbers: List[int] = Field(description="Specific line numbers affected by the bug.")
    code_snippet: Optional[str] = Field(description="The relevant code block where the bug is located.")
    description: str = Field(description="A detailed description of the potential bug, including why it's a bug.")
    severity: Literal["Critical", "High", "Medium", "Low"] = Field(description="Severity of the bug.")
    suggested_fix: str = Field(description="Concrete suggestion on how to fix the bug.")

class BugDetectionAgentOutput(BaseModel):
    has_bugs: bool = Field(description="True if any bugs were detected, False otherwise.")
    findings: List[BugFinding] = Field(description="List of detected bugs with details.")
    overall_assessment: str = Field(description="An overall summary of the bug risk in the PR, considering the conversation context.")

class CodeQualitySuggestion(BaseModel):
    file: str = Field(description="The file path where the suggestion applies.")
    line_numbers: Optional[List[int]] = Field(description="Specific line numbers for the suggestion, if applicable.")
    code_block: Optional[str] = Field(description="The relevant code block for the suggestion.")
    description: str = Field(description="A detailed explanation of the code quality issue.")
    suggestion: str = Field(description="Specific, actionable advice to improve code quality.")
    category: Literal["Readability", "Maintainability", "Performance", "Best Practice", "Duplication", "Clarity"] = Field(description="Category of the code quality suggestion.")

class CodeQualityAgentOutput(BaseModel):
    code_quality_score: int = Field(description="An overall score (1-100) indicating the code quality, where higher is better.")
    suggestions: List[CodeQualitySuggestion] = Field(description="List of detailed code quality improvement suggestions.")
    summary_comment: str = Field(description="A concise summary of the code quality review, highlighting strengths and weaknesses.")

class SecurityFinding(BaseModel):
    file: str = Field(description="The file path where the security vulnerability was found.")
    line_numbers: Optional[List[int]] = Field(description="Specific line numbers affected by the vulnerability.")
    code_snippet: Optional[str] = Field(description="The relevant code block containing the vulnerability.")
    title: str = Field(description="Short description of the issue (e.g., \"Hardcoded API Key\", \"SQL Injection Vulnerability\").")
    explanation: str = Field(description="Detailed reasoning why it’s a security problem and potential impact.")
    risk_level: Literal["Critical", "High", "Medium", "Low", "Informational"] = Field(description="Severity of the security risk.")
    recommended_mitigation: str = Field(description="Specific steps or patterns to mitigate the security vulnerability.")

class SecurityAgentOutput(BaseModel):
    has_security_vulnerabilities: bool = Field(description="True if any security vulnerabilities were detected, False otherwise.")
    findings: List[SecurityFinding] = Field(description="List of detected security vulnerabilities with details.")
    overall_security_assessment: str = Field(description="An overall summary of the security posture of the changes.")

class AlignmentAgentOutput(BaseModel):
    alignment_score: int = Field(description="A score (0-100) indicating how well the PR aligns with the repository's purpose and goals.")
    classification: Literal["Core Improvement", "Feature Addition", "Bug Fix", "Refactoring", "Documentation", "Peripheral", "Off-topic"] = Field(description="Classification of the PR's alignment.")
    justification: str = Field(description="Detailed explanation of why the PR aligns or deviates from the repository's goals, referencing the PR message and repo context.")
    potential_misalignment_risks: List[str] = Field(description="Any identified risks or concerns regarding the PR's long-term alignment with the project's vision.")

class PullRequestReviewReport(BaseModel):
    overall_verdict: Literal["Approved", "Changes Requested", "Needs More Review"] = Field(description="Final recommendation for the pull request.")
    executive_summary: str = Field(description="A high-level summary of the PR review, suitable for project managers or leads.")
    bug_risk_summary: str = Field(description="Summary of bug detection findings.")
    code_quality_summary: str = Field(description="Summary of code quality findings and overall assessment.")
    security_summary: str = Field(description="Summary of security findings and overall assessment.")
    alignment_summary: str = Field(description="Summary of how well the PR aligns with project goals.")
    detailed_findings: Dict[str, Any] = Field(description="A dictionary containing the detailed findings from each specialized agent (BugDetectionAgentOutput, CodeQualityAgentOutput, etc.).")
    committer_feedback: str = Field(description="A human-like, constructive comment for the PR committer, summarizing key takeaways, areas of focus for improvement, and overall sentiment. This should sound like a personal review.")
    actionable_next_steps_for_committer: List[str] = Field(description="Specific, actionable next steps for the committer to address identified issues or improve the PR.")

