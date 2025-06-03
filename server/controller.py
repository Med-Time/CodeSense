import asyncio
import json
from crewai import Crew, Process
from pydantic import ValidationError, BaseModel
from typing import Dict, Any

# Import agents and tasks from crew_agents.py
from crew_agents import (
    RepoContextAgent, BugDetectionAgent, CodeQualityAgent,
    SecurityAgent, AlignmentAgent, ReportCompilerAgent,
    RepoContextAgent_task, BugDetectionAgent_task, CodeQualityAgent_task,
    SecurityAgent_task, AlignmentAgent_task, ReportCompilerAgent_task
)

# Import utility for input preparation
from utils import prepare_agent_inputs_from_pr_url

# Import Pydantic models for agent outputs
from models import (
    RepoContextAgentOutput,
    BugDetectionAgentOutput,
    CodeQualityAgentOutput,
    SecurityAgentOutput,
    AlignmentAgentOutput,
    PullRequestReviewReport
)

def clean_agent_output(output: str) -> str:
    """
    Clean agent output by removing markdown code block formatting.
    """
    # Remove markdown code block markers
    if output.startswith("```") and output.endswith("```"):
        # Extract language identifier if present
        first_line_end = output.find("\n")
        if first_line_end > 0:
            language = output[3:first_line_end].strip()
            # Remove first line (```json) and last line (```)
            output = output[first_line_end + 1:output.rindex("```")].strip()
    
    return output

async def run_pr_review_crew(pr_url: str) -> Dict[str, Any]:
    """
    Orchestrates the entire PR review process using CrewAI.
    Fetches PR data, runs agents, and compiles a final report.
    """
    print(f"Starting PR review for URL: {pr_url}")

    try:
        # Step 1: Prepare all inputs from the PR URL
        inputs = await prepare_agent_inputs_from_pr_url(pr_url)
        
        repo_context_inputs = {
            'repository_structure': inputs['repository_structure'],
            'repository_contents': inputs['repository_contents'],
            'pr_conversation_initial_message': inputs['pr_conversation_initial_message']
        }

        level_2_base_inputs = {
            'all_pr_diffs': inputs['all_pr_diffs'],
            'all_original_pr_files': inputs['all_original_pr_files'],
            'pr_conversation_initial_message': inputs['pr_conversation_initial_message']
        }

        # Step 2: Run Crew 1: RepoContextAgent
        print("🚀 Running Crew 1: Repo Context Agent")
        crew_1 = Crew(
            agents=[RepoContextAgent],
            tasks=[RepoContextAgent_task],
            verbose=True,
            full_output=True # Get full output to parse pydantic
        )
        
        # CrewAI's kickoff method is not async-compatible, so run it in a thread pool
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result_1_raw = await asyncio.get_event_loop().run_in_executor(
                pool, lambda: crew_1.kickoff(inputs=repo_context_inputs)
            )
        
        # Handle potential non-Pydantic output from kickoff
        repo_context_result: RepoContextAgentOutput
        try:
            repo_context_result = RepoContextAgentOutput.parse_raw(result_1_raw.raw)
        except ValidationError as e:
            print(f"Warning: RepoContextAgent did not return a valid Pydantic model directly. Attempting conversion from string. Error: {e}")
            try:
                # If it's a string, try loading as JSON and then parsing
                repo_context_result = RepoContextAgentOutput.parse_obj(json.loads(result_1_raw.raw))
            except (json.JSONDecodeError, ValidationError) as e:
                print(f"Error parsing RepoContextAgent output: {e}. Falling back to default.")
                repo_context_result = RepoContextAgentOutput(
                    repo_purpose_summary=str(result_1_raw.raw),
                    key_modules_concerns_goals=[],
                    technologies_used=[],
                    common_patterns_conventions=[],
                    pr_message_context_summary=inputs['pr_conversation_initial_message']
                )

        print(f"✅ Crew 1 Result (Repo Context): {repo_context_result.model_dump_json()}")

        # Step 3: Prepare inputs for Level 2 agents with repo context
        enhanced_level_2_inputs = {
            **level_2_base_inputs,
            'repo_context': repo_context_result.model_dump_json()
        }

        # Step 4: Run Level 2 agents in parallel
        print("🚀 Running Level 2 Crews (Bug, Quality, Security, Alignment) in parallel")

        crew_2 = Crew(agents=[CodeQualityAgent], tasks=[CodeQualityAgent_task], verbose=True, full_output=True)
        crew_3 = Crew(agents=[BugDetectionAgent], tasks=[BugDetectionAgent_task], verbose=True, full_output=True)
        crew_4 = Crew(agents=[SecurityAgent], tasks=[SecurityAgent_task], verbose=True, full_output=True)
        crew_5 = Crew(agents=[AlignmentAgent], tasks=[AlignmentAgent_task], verbose=True, full_output=True)

        # Run them in thread pool since CrewAI doesn't support native async
        with concurrent.futures.ThreadPoolExecutor() as pool:
            tasks = [
                asyncio.get_event_loop().run_in_executor(pool, lambda: crew_2.kickoff(inputs=enhanced_level_2_inputs)),
                asyncio.get_event_loop().run_in_executor(pool, lambda: crew_3.kickoff(inputs=enhanced_level_2_inputs)),
                asyncio.get_event_loop().run_in_executor(pool, lambda: crew_4.kickoff(inputs=enhanced_level_2_inputs)),
                asyncio.get_event_loop().run_in_executor(pool, lambda: crew_5.kickoff(inputs=enhanced_level_2_inputs))
            ]
            results = await asyncio.gather(*tasks)
            result_2_raw, result_3_raw, result_4_raw, result_5_raw = results

        # Parse Pydantic outputs with robust error handling
        result_2_parsed = None
        result_3_parsed = None
        result_4_parsed = None
        result_5_parsed = None

        try:
            # Clean and parse result_2_raw (CodeQualityAgent)
            cleaned_output = clean_agent_output(result_2_raw.raw)
            result_2_parsed = CodeQualityAgentOutput.parse_raw(cleaned_output)
        except (ValidationError, json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing CodeQualityAgent output: {e}")
            # Create a fallback object
            result_2_parsed = CodeQualityAgentOutput(
                has_code_quality_issues=False,
                findings=[],
                overall_code_quality_assessment="Unable to parse code quality assessment"
            )

        try:
            # Clean and parse result_3_raw (BugDetectionAgent)
            cleaned_output = clean_agent_output(result_3_raw.raw)
            result_3_parsed = BugDetectionAgentOutput.parse_raw(cleaned_output)
        except (ValidationError, json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing BugDetectionAgent output: {e}")
            # Create a fallback object
            result_3_parsed = BugDetectionAgentOutput(
                has_bugs=False,
                findings=[],
                overall_assessment="Unable to parse bug detection assessment"
            )

        try:
            # Clean and parse result_4_raw (SecurityAgent) 
            cleaned_output = clean_agent_output(result_4_raw.raw)
            result_4_parsed = SecurityAgentOutput.parse_raw(cleaned_output)
        except (ValidationError, json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing SecurityAgent output: {e}")
            # Create a fallback object
            result_4_parsed = SecurityAgentOutput(
                has_security_vulnerabilities=False,
                findings=[],
                overall_security_assessment="Unable to parse security assessment"
            )

        try:
            # Clean and parse result_5_raw (AlignmentAgent)
            cleaned_output = clean_agent_output(result_5_raw.raw)
            result_5_parsed = AlignmentAgentOutput.parse_raw(cleaned_output)
        except (ValidationError, json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing AlignmentAgent output: {e}")
            # Create a fallback object
            result_5_parsed = AlignmentAgentOutput(
                alignment_score=50,
                pr_nature_classification="Core Improvement",
                justification="Unable to parse alignment assessment",
                potential_misalignment_risks=[]
            )

        # Step 5: Run Crew 6: ReportCompilerAgent
        print("🚀 Running Crew 6: Report Compiler Agent")
        crew_6_inputs = {
            "repo_context_result": repo_context_result.model_dump_json(),
            "bug_detection_result": result_3_parsed.model_dump_json(),
            "code_quality_result": result_2_parsed.model_dump_json(), 
            "security_result": result_4_parsed.model_dump_json(),
            "alignment_result": result_5_parsed.model_dump_json(),
            "pr_conversation_initial_message": inputs['pr_conversation_initial_message']
        }
        
        crew_6 = Crew(
            agents=[ReportCompilerAgent],
            tasks=[ReportCompilerAgent_task],
            verbose=True,
            full_output=True
        )
        
        # Run in thread pool
        with concurrent.futures.ThreadPoolExecutor() as pool:
            final_report_raw = await asyncio.get_event_loop().run_in_executor(
                pool, lambda: crew_6.kickoff(inputs=crew_6_inputs)
            )

        # Debug the raw output
        print("\n==== RAW FINAL REPORT ====")
        print(final_report_raw.raw)
        print("==== END RAW FINAL REPORT ====\n")

        try:
            # Clean the final report output just like we did with other agents
            cleaned_final_report = clean_agent_output(final_report_raw.raw)
            
            # Debug the cleaned output
            print("\n==== CLEANED FINAL REPORT ====")
            print(cleaned_final_report)
            print("==== END CLEANED FINAL REPORT ====\n")
            
            # Parse the cleaned output
            final_report = PullRequestReviewReport.parse_raw(cleaned_final_report)
            
            # Return the compiled report
            return final_report.model_dump()
        except (ValidationError, json.JSONDecodeError) as e:
            print(f"Error parsing final report: {e}")
            # Create a fallback report
            fallback_report = PullRequestReviewReport(
                overall_verdict="Unable to generate complete report due to parsing error",
                review_summary="An error occurred during the final report generation. Please check the logs for details.",
                key_findings=[
                    "Error in report compilation process",
                    f"Error details: {str(e)}"
                ],
                code_quality_summary="See partial results in console output",
                security_review_summary="See partial results in console output", 
                bug_risk_summary="See partial results in console output",
                alignment_assessment="See partial results in console output",
                suggested_changes=[
                    "Please try rerunning the review or check individual agent outputs"
                ]
            )
            
            return fallback_report.model_dump()
    except Exception as e:
        print(f"❌ An error occurred during PR review: {e}")
        raise

# Add a simple HTTPException for better error handling in FastAPI
from fastapi import HTTPException