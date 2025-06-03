import os
from crewai import Crew, Agent, Task, LLM
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import json

# Import Pydantic models from your models.py
from models import (
    RepoContextAgentOutput,
    BugDetectionAgentOutput, BugFinding,
    CodeQualityAgentOutput, CodeQualitySuggestion,
    SecurityAgentOutput, SecurityFinding,
    AlignmentAgentOutput,
    PullRequestReviewReport
)

load_dotenv()

# Configure Gemini LLM
gemini_llm = LLM(
    model="gemini/gemini-1.5-flash",
    temperature=0.0, # Keep temperature low for more deterministic analysis
    api_key=os.getenv("GEMINI_API_KEY"),
)

# --- Define Agents ---
RepoContextAgent = Agent(
    role="Software Architecture Investigator",
    goal="Analyze the structure and intent of a codebase to understand its core logic, purpose, and components, and to summarize the PR's overall context.",
    backstory=""" You're a senior software analyst with deep experience in reverse-engineering large-scale applications.
    Your ability to dissect a project's purpose and architecture from its file structure and documentation is unparalleled.
    You also excel at synthesizing the committer's own explanation for changes, providing invaluable context for subsequent analysis.
    """,
    llm=gemini_llm,
    verbose=True,
    allow_delegation=False,
)

BugDetectionAgent = Agent(
    role="Bug and Logic Error Detector",
    goal="Identify potential bugs, logical errors, edge cases, and performance issues across the entire pull request, considering inter-file interactions.",
    backstory="""You are a meticulous software quality assurance engineer. You have a keen eye for detail and
    can spot subtle logical flaws, off-by-one errors, concurrency issues, and performance bottlenecks
    even in complex codebases. You are adept at identifying how changes in one file might
    unintentionally affect others, leading to system-wide issues.
    """,
    llm=gemini_llm,
    verbose=True,
    allow_delegation=False,
)

CodeQualityAgent = Agent(
    role="Code Style and Maintainability Reviewer",
    goal="Evaluate code quality, readability, maintainability, and adherence to best practices for the entire pull request.",
    backstory="""You are a seasoned software architect and maintainer, passionate about clean code.
    You advocate for readability, modularity, and adherence to established coding standards.
    You provide constructive feedback aimed at improving the long-term health and understanding of the codebase.
    You understand that different technologies have different best practices and tailor your advice accordingly.
    """,
    llm=gemini_llm,
    verbose=True,
    allow_delegation=False,
)

SecurityAgent = Agent(
    role="Software Security Auditor",
    goal="Identify security vulnerabilities, insecure patterns, and potential attack vectors within the pull request.",
    backstory="""You are a cybersecurity expert with a deep understanding of common vulnerabilities
    (OWASP Top 10, etc.) and secure coding principles. You can pinpoint weaknesses in authorization,
    authentication, input validation, and data handling that could expose the system to risks.
    You are constantly thinking like an attacker to proactively find and recommend mitigations for flaws.
    """,
    llm=gemini_llm,
    verbose=True,
    allow_delegation=False,
)

AlignmentAgent = Agent(
    role="Project Vision Aligner",
    goal="Assess whether the pull request aligns with the overall purpose, goals, and architectural vision of the repository.",
    backstory="""You are a strategic technical lead who ensures that all changes contribute positively
    to the project's long-term vision. You evaluate if the PR's nature and changes are consistent
    with the core objectives and architectural patterns, identifying potential scope creep or
    deviation from the intended path.
    """,
    llm=gemini_llm,
    verbose=True,
    allow_delegation=False,
)

ReportCompilerAgent = Agent(
    role="PR Review Report Compiler",
    goal="Synthesize findings from all review agents into a comprehensive, actionable, and human-friendly pull request review report.",
    backstory="""You are a master communicator, capable of consolidating complex technical feedback
    into clear, concise, and empathetic reports. You prioritize findings, provide an overall verdict,
    and craft actionable next steps, ensuring the committer receives constructive guidance.
    You always start with positive reinforcement and build rapport.
    """,
    llm=gemini_llm,
    verbose=True,
    allow_delegation=False,
)


# --- Define Tasks ---

# RepoContextAgent_task (No change in inputs, as it already takes overall context)
RepoContextAgent_task = Task(
    description=(
        "Given the `{repository_structure}` (file paths and names), `{repository_contents}` (README.md, etc.), "
        "and crucially, the `{pr_conversation_initial_message}` which provides the committer's own explanation "
        "and context for the pull request:\n\n"
        "1. **Summarize the overall purpose of the repository/project.** What problem does it solve? What is its domain?\n"
        "2. **Identify key modules, architectural patterns, and primary goals.** Based on the file structure and README, "
        "what are the main functional areas or design principles?\n"
        "3. **Detect major technologies, frameworks, and languages used.** (e.g., Python, React, Flask, Django, etc.).\n"
        "4. **Identify common coding conventions or best practices evident in the repository.** (e.g., 'Uses functional components in React', 'Follows PEP8 for Python').\n"
        "5. **Carefully read and synthesize the `{pr_conversation_initial_message}`.** Extract the committer's stated intent, the problem this PR aims to solve, and the high-level approach taken. This is critical for understanding the context of the changes from the author's perspective.\n\n"
        "Your output must be a well-structured Pydantic object, ensuring all fields are populated with detailed and insightful information."
    ),
    output_pydantic=RepoContextAgentOutput,
    expected_output=RepoContextAgentOutput.schema_json(),
    agent=RepoContextAgent,
    # output_file="output/repo_context_agent_output.json", # Remove output_file for API use
)

# BugDetectionAgent_task - Updated for whole-PR analysis
BugDetectionAgent_task = Task(
    description=(
        "Analyze the **entire pull request**, which consists of `all_pr_diffs` (a JSON string representing an array of changes for multiple files) "
        "and `all_original_pr_files` (a JSON string representing an object mapping filenames to their original content before the changes). "
        "Your goal is to identify any potential bugs, logical errors, edge case failures, or bad practices that could lead to "
        "runtime issues across the *entire scope of the pull request*.\n\n"
        "**Crucially, use the `{repo_context}` provided by the 'Software Architecture Investigator' to understand "
        "the project's domain, typical operations, and expected behaviors.** "
        "Also, consider the `{pr_conversation_initial_message}` to understand the committer's intent for the PR as a whole, "
        "which can help in identifying if the introduced changes meet their stated purpose without bugs, especially when "
        "considering interactions between files.\n\n"
        "Focus on:\n"
        "- Bugs within individual changed files.\n"
        "- **Inter-file bugs**: logical errors or regressions that arise from how changes in one file interact with changes in another (e.g., mismatched API contracts, inconsistent state management).\n"
        "- Off-by-one errors, infinite loops, incorrect conditional logic.\n"
        "- Resource leaks (e.g., unclosed files, unreleased locks).\n"
        "- Race conditions or concurrency issues introduced by the PR.\n"
        "- Incorrect handling of edge cases (nulls, empty inputs, large values) across the PR's scope.\n"
        "- Type mismatches or unexpected data conversions *between* modules affected by the PR.\n"
        "- Performance bottlenecks introduced by the PR's overall changes.\n"
        "- Any deviation from the `{repo_context}` that might introduce unforeseen bugs across the system.\n\n"
        "For each potential bug, provide:\n"
        "1. The `file` name (even if the bug spans multiple files, identify the primary affected file/module).\n"
        "2. `line_numbers` where the issue is found.\n"
        "3. The exact `code_snippet` (if applicable).\n"
        "4. A clear `description` of the bug and why it's a problem, including how it might affect other parts of the PR or system.\n"
        "5. The `severity` (Critical, High, Medium, Low).\n"
        "6. A `suggested_fix` that is concrete and actionable.\n\n"
        "If no bugs are found, set `has_bugs` to `False` and `findings` as an empty list, and provide an `overall_assessment` that confirms a low bug risk for the pull request.\n"
        "Your output must adhere to the `BugDetectionAgentOutput` Pydantic model."
    ),
    output_pydantic=BugDetectionAgentOutput,
    expected_output=BugDetectionAgentOutput.schema_json(),
    agent=BugDetectionAgent,
    # output_file="output/bug_detection_agent_output.json",
)

# CodeQualityAgent_task - Updated for whole-PR analysis
CodeQualityAgent_task = Task(
    description=(
        "Review the **entire pull request**, analyzing `all_pr_diffs` (a JSON string of changes) and `all_original_pr_files` (a JSON string of original contents) for code quality issues. "
        "**Refer to the `{repo_context}` provided by the 'Software Architecture Investigator', "
        "especially `technologies_used` and `common_patterns_conventions`, to ensure your suggestions are relevant to the project's ecosystem.** "
        "Also, consider the `{pr_conversation_initial_message}` to understand the committer's intent, "
        "allowing for context-aware suggestions across the PR.\n\n"
        "Focus on:\n"
        "- Readability and clarity (e.g., variable names, comments, code structure) across all changed files.\n"
        "- Maintainability (e.g., modularity, coupling, complexity) of the introduced changes and their impact on the system.\n"
        "- Adherence to established best practices for the identified technologies, ensuring consistency across new and existing code.\n"
        "- Efficiency and performance considerations (avoiding obvious inefficiencies) in the context of the PR's overall changes.\n"
        "- Code duplication, especially across new or modified files.\n"
        "- Error handling and defensive programming, ensuring robustness throughout the PR's scope.\n\n"
        "Provide a `code_quality_score` (1-100) and a list of `suggestions`. "
        "For each suggestion, specify the `file`, `line_numbers`, `code_block`, `description`, `suggestion` (actionable advice), and `category`.\n"
        "Summarize the overall code quality assessment in `summary_comment`.\n"
        "Your output must adhere to the `CodeQualityAgentOutput` Pydantic model."
    ),
    output_pydantic=CodeQualityAgentOutput,
    expected_output=CodeQualityAgentOutput.schema_json(),
    agent=CodeQualityAgent,
    # output_file="output/code_quality_agent_output.json",
)

# SecurityAgent_task - Updated for whole-PR analysis
SecurityAgent_task = Task(
    description=(
        "Analyze the **entire pull request**, considering `all_pr_diffs` (a JSON string of changes) and `all_original_pr_files` (a JSON string of original contents) for any security vulnerabilities or risks. "
        "**Use the `{repo_context}` to understand the project's technologies (`technologies_used`) and typical data flows, "
        "which can help identify common security pitfalls relevant to this codebase.** "
        "Consider the `{pr_conversation_initial_message}` to see if the changes impact any security-sensitive areas as described by the committer, and look for inter-file security implications.\n\n"
        "Focus on:\n"
        "- Hardcoded credentials or sensitive information.\n"
        "- Injection vulnerabilities (SQL, XSS, Command Injection, etc.) across the PR's scope.\n"
        "- Broken authentication or authorization issues introduced or exacerbated by the changes.\n"
        "- Insecure deserialization.\n"
        "- Cross-Site Request Forgery (CSRF) vulnerabilities.\n"
        "- Misconfigurations or insecure default settings related to the PR.\n"
        "- Use of vulnerable third-party libraries (if discernible from code dependencies).\n"
        "- Insufficient input validation or output encoding, especially at integration points introduced by the PR.\n"
        "- Denial of Service (DoS) vulnerabilities.\n\n"
        "For each finding, provide the `file`, `line_numbers`, `code_snippet`, `title`, `explanation`, `risk_level` (Critical, High, Medium, Low, Informational), and `recommended_mitigation`.\n"
        "If no vulnerabilities are found, set `has_security_vulnerabilities` to `False` and `findings` as an empty list, and provide an `overall_security_assessment` that confirms a low security risk for the pull request.\n"
        "Your output must adhere to the `SecurityAgentOutput` Pydantic model."
    ),
    output_pydantic=SecurityAgentOutput,
    expected_output=SecurityAgentOutput.schema_json(),
    agent=SecurityAgent,
    # output_file="output/security_agent_output.json",
)

# AlignmentAgent_task - Updated for whole-PR analysis
AlignmentAgent_task = Task(
    description=(
        "Evaluate the **entire pull request**, considering `all_pr_diffs` (a JSON string of changes) and, critically, "
        "the `{pr_conversation_initial_message}` against the `{repo_context}` provided by "
        "the 'Software Architecture Investigator'.\n\n"
        "1. **Determine the `alignment_score` (0-100)**: How well do these changes (and their stated purpose) fit with the repository purpose and key modules/goals as described in the repo context? Consider the holistic impact of all changes.\n"
        "2. **Classify the PR's nature**: Is it a 'Core Improvement', 'Feature Addition', 'Bug Fix', 'Refactoring', 'Documentation', 'Peripheral' (related but not core), or 'Off-topic'? Use the PR message as primary guidance.\n"
        "3. **Provide a detailed `justification`**: Explain *why* the PR aligns or deviates, referencing specific points from the `{repo_context}` and the `{pr_conversation_initial_message}`. "
        "Explain how the *combined changes* contribute to or detract from the project's overall vision.\n"
        "4. **Identify `potential_misalignment_risks`**: Are there any long-term risks if this type of change is frequently introduced? Does it set a precedent that could lead to architectural debt or scope creep, considering the entire scope of the PR?\n\n"
        "Your output must strictly follow the `AlignmentAgentOutput` Pydantic model."
    ),
    output_pydantic=AlignmentAgentOutput,
    expected_output=AlignmentAgentOutput.schema_json(),
    agent=AlignmentAgent,
    # output_file="output/alignment_agent_output.json",
)

# ReportCompilerAgent_task (No change in inputs, as it collects results from other agents)
ReportCompilerAgent_task = Task(
    description=(
        "Collect and synthesize the results from the `{repo_context_result}`, `{bug_detection_result}`, "
        "`{code_quality_result}`, `{security_result}`, and `{alignment_result}`. "
        "Also, use the `{pr_conversation_initial_message}` to ensure the final feedback is contextually relevant and addresses the committer's stated intent.\n\n"
        "Your primary goal is to generate a `PullRequestReviewReport` that includes:\n"
        "1. **`overall_verdict`**: Your final recommendation (Approved, Changes Requested, Needs More Review).\n"
        "2. **`executive_summary`**: A high-level summary of the PR's overall state, suitable for project managers or leads.\n"
        "3. **Summaries for each area**: `bug_risk_summary`, `code_quality_summary`, `security_summary`, `alignment_summary`.\n"
        "4. **`detailed_findings`**: Include the full Pydantic outputs from all sub-agents for completeness.\n"
        "5. **`committer_feedback`**: This is CRITICAL. Craft a *human-like, empathetic, and constructive comment* that directly addresses the committer. "
        "Start with positive feedback where appropriate. Then, clearly but kindly, explain any identified issues, "
        "referencing specific findings from the other agents. "
        "This comment should sound like a personal review from a helpful mentor. "
        "Acknowledge their stated goal from the `{pr_conversation_initial_message}`.\n"
        "6. **`actionable_next_steps_for_committer`**: A bulleted list of concrete, prioritized actions the committer should take to address identified issues or improve the PR. This should be derived directly from the findings and suggestions of the other agents.\n\n"
        "Ensure the final output is a Markdown report, suitable for direct pasting into a pull request comment. "
        "The `committer_feedback` should be the most prominent and carefully crafted part of your response, emphasizing actionable improvements.\n"
        "Your output must strictly adhere to the `PullRequestReviewReport` Pydantic model. **Do not include any additional prose outside the Pydantic model.**"
    ),
    output_pydantic=PullRequestReviewReport,
    expected_output=PullRequestReviewReport.schema_json(),
    agent=ReportCompilerAgent,
    # output_file="output/report_compiler_agent_output.json",
)