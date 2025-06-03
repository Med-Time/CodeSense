import os
import re
import requests
import json
from github import Github, UnknownObjectException, GithubException
from langchain_community.document_loaders import GithubFileLoader
import tempfile
import subprocess
from typing import List, Dict, Any, Optional, Literal

GITHUB_API = "https://api.github.com"

# --- GitHub Client ---
def get_github_client():
    # Ensure dotenv is loaded here if this file is run independently for testing,
    # otherwise, it can be loaded in main.py once.
    # from dotenv import load_dotenv
    # load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    return Github(token) if token else Github()

# --- Get Repo Object ---
def get_repo(repo_full_name: str):
    try:
        client = get_github_client()
        return client.get_repo(repo_full_name)
    except GithubException as e:
        raise Exception(f"Failed to access repository '{repo_full_name}': {e}")

def parse_github_pr_url(pr_url: str):
    """
    Extracts owner, repo, and PR number from a GitHub PR URL.
    """
    match = re.match(
        r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<pr_number>\d+)",
        pr_url
    )
    if not match:
        raise ValueError("Invalid GitHub PR URL")
    return match.group("owner"), match.group("repo"), int(match.group("pr_number"))

def chunk_diff(patch: str):
    """
    Extracts both added and removed lines from a unified diff patch.
    Returns two lists: added_chunks and removed_chunks
    """
    added_chunks = []
    removed_chunks = []

    if not patch:
        return added_chunks, removed_chunks

    lines = patch.split('\n')
    added_chunk = []
    removed_chunk = []
    added_lines = []
    removed_lines = []

    old_line = new_line = 0

    for line in lines:
        # Start of a diff hunk
        if line.startswith('@@'):
            if added_chunk:
                added_chunks.append({
                    "lines": added_lines,
                    "code": "\n".join(added_chunk)
                })
                added_chunk = []
                added_lines = []

            if removed_chunk:
                removed_chunks.append({
                    "lines": removed_lines,
                    "code": "\n".join(removed_chunk)
                })
                removed_chunk = []
                removed_lines = []

            match = re.match(r"@@ -(\d+),?\d* \+(\d+),?\d* @@", line)
            if match:
                old_line = int(match.group(1))
                new_line = int(match.group(2))
        elif line.startswith('+') and not line.startswith('+++'):
            added_chunk.append(line[1:])
            added_lines.append(new_line)
            new_line += 1
        elif line.startswith('-') and not line.startswith('---'):
            removed_chunk.append(line[1:])
            removed_lines.append(old_line)
            old_line += 1
        else:
            # Context line
            if added_chunk:
                added_chunks.append({
                    "lines": added_lines,
                    "code": "\n".join(added_chunk)
                })
                added_chunk = []
                added_lines = []
            if removed_chunk:
                removed_chunks.append({
                    "lines": removed_lines,
                    "code": "\n".join(removed_chunk)
                })
                removed_chunk = []
                removed_lines = []
            old_line += 1
            new_line += 1

    # Final pending chunks
    if added_chunk:
        added_chunks.append({
            "lines": added_lines,
            "code": "\n".join(added_chunk)
        })
    if removed_chunk:
        removed_chunks.append({
            "lines": removed_lines,
            "code": "\n".join(removed_chunk)
        })

    return added_chunks, removed_chunks


def fetch_pr_diff_and_content(repo_owner: str, repo_name: str, pr_number: int, token: Optional[str] = None):
    """
    Fetches PR file changes (diffs) and their original content.
    Returns a list of dictionaries, each containing file, original_content, added, and removed.
    """
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    files_url = f"{GITHUB_API}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
    response = requests.get(files_url, headers=headers)
    response.raise_for_status()
    files_data = response.json()

    repo = get_repo(f"{repo_owner}/{repo_name}")
    pr = repo.get_pull(pr_number)

    all_file_changes = []
    for file_info in files_data:
        filename = file_info['filename']
        patch = file_info.get('patch')

        original_content = ""
        try:
            # Try to get the content of the file from the base branch before the PR
            content_obj = repo.get_contents(filename, ref=pr.base.ref)
            # Check if the content is not binary (can be decoded as text)
            if content_obj.encoding == 'base64':
                try:
                    original_content = content_obj.decoded_content.decode('utf-8')
                except UnicodeDecodeError:
                    # Handle files that can't be decoded as UTF-8 text
                    print(f"Note: File {filename} appears to be binary, skipping content extraction")
                    original_content = "[Binary file content not shown]"
            else:
                print(f"Warning: Unsupported encoding '{content_obj.encoding}' for {filename}")
                original_content = f"[Content with encoding {content_obj.encoding} not shown]"
        except Exception as e:
            print(f"Warning: Could not fetch original content for {filename} from base branch: {e}")
            original_content = "" # Or handle as appropriate

        added_chunks, removed_chunks = chunk_diff(patch) if patch else ([], [])

        all_file_changes.append({
            "file": filename,
            "original_content": original_content,
            "added": added_chunks,
            "removed": removed_chunks
        })
    return all_file_changes

def fetch_pr_conversation(repo_owner: str, repo_name: str, pr_number: int, token: Optional[str] = None):
    """
    Fetches the initial PR message and subsequent comments.
    Returns a list of dicts, including 'body' for the main PR message.
    """
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Fetch main PR details for the initial message
    pr_url = f"{GITHUB_API}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
    pr_response = requests.get(pr_url, headers=headers)
    pr_response.raise_for_status()
    pr_data = pr_response.json()

    conversation_messages = []
    if pr_data.get("body"):
        conversation_messages.append({
            "user": pr_data["user"]["login"],
            "created_at": pr_data.get("created_at"),
            "body": pr_data["body"]
        })

    # Fetch comments (optional, but good for full context)
    comments_url = f"{GITHUB_API}/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
    comments_response = requests.get(comments_url, headers=headers)
    comments_response.raise_for_status()
    comments_data = comments_response.json()

    for comment in comments_data:
        conversation_messages.append({
            "user": comment["user"]["login"],
            "created_at": comment.get("created_at"),
            "body": comment["body"]
        })
    return conversation_messages

def get_repository_structure_and_content(repo_owner: str, repo_name: str, branch: str = "HEAD", token: Optional[str] = None):
    """
    Fetches the repository structure (file paths) and README.md content.
    For more comprehensive repo content, this might need cloning or deeper API calls.
    """
    repo = get_repo(f"{repo_owner}/{repo_name}")
    
    # Fetch repository structure (file paths)
    tree = repo.get_git_tree(sha=branch, recursive=True)
    repository_structure = "\n".join([f.path for f in tree.tree if f.type == 'blob'])

    # Fetch README.md content
    readme_content = ""
    try:
        readme = repo.get_readme()
        readme_content = readme.decoded_content.decode('utf-8')
    except UnknownObjectException:
        print("No README.md found in the repository.")
        readme_content = "No README.md available."
    except Exception as e:
        print(f"Error fetching README.md: {e}")
        readme_content = "Error fetching README.md content."
    
    repository_contents = f"README.md:\n{readme_content}\n\n"
    # You could add other important files here, e.g., package.json, requirements.txt
    # by fetching them similarly.

    return repository_structure, repository_contents

async def prepare_agent_inputs_from_pr_url(pr_url: str) -> Dict[str, Any]:
    """
    Prepares all inputs needed for PR review agents from a GitHub PR URL.
    """
    try:
        # Parse the PR URL
        repo_owner, repo_name, pr_number = parse_github_pr_url(pr_url)

        # Get GitHub token from environment variables
        github_token = os.getenv("GITHUB_TOKEN")

        if not github_token:
            print("⚠️ Warning: GITHUB_TOKEN not found in environment variables. API rate limits may apply.")
            
        # Add retry logic with exponential backoff
        max_retries = 3
        retry_delay = 2  # starting delay in seconds
        
        for attempt in range(max_retries):
            try:
                # Fetch PR diff and content
                file_changes = fetch_pr_diff_and_content(
                    repo_owner, repo_name, pr_number, token=github_token
                )
                
                # Fetch PR conversation
                pr_conversation = fetch_pr_conversation(
                    repo_owner, repo_name, pr_number, token=github_token
                )
                
                # Get repository structure and content
                repo_structure, repo_contents = get_repository_structure_and_content(
                    repo_owner, repo_name, token=github_token
                )
                
                # Successfully retrieved all data
                break
                
            except Exception as e:
                if "rate limit exceeded" in str(e).lower() and attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"⚠️ GitHub API rate limit reached. Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
                else:
                    # Re-raise the exception if it's not a rate limit issue or we've exhausted retries
                    raise
        
        # Process file changes
        all_pr_diffs = json.dumps([{
            "file": fc["file"],
            "added": fc["added"],
            "removed": fc["removed"]
        } for fc in file_changes])
        
        all_original_pr_files = json.dumps([{
            "file": fc["file"],
            "content": fc["original_content"]
        } for fc in file_changes])
        
        # Extract initial PR comment if available, otherwise use a placeholder
        pr_conversation_initial_message = "No description provided."
        if pr_conversation and len(pr_conversation) > 0:
            pr_conversation_initial_message = pr_conversation[0]["body"] or "No description provided."
        
        return {
            "repository_structure": json.dumps(repo_structure),
            "repository_contents": json.dumps(repo_contents),
            "all_pr_diffs": all_pr_diffs,
            "all_original_pr_files": all_original_pr_files,
            "pr_conversation_initial_message": pr_conversation_initial_message
        }
        
    except Exception as e:
        print(f"Error preparing agent inputs: {e}")
        raise