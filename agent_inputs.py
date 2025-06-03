import os
from dotenv import load_dotenv
from github import Github, UnknownObjectException, GithubException
from langchain_community.document_loaders import GithubFileLoader
from pprint import pprint
from core.fetcher import fetch_pr_diff
from core.fetcher import fetch_pr_conversation
import json

# --- GitHub Client ---
def get_github_client():
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    return Github(token) if token else Github()

# --- Get Repo Object ---
def get_repo(repo_full_name: str):
    try:
        client = get_github_client()
        return client.get_repo(repo_full_name)
    except GithubException as e:
        raise Exception(f"Failed to access repository '{repo_full_name}': {e}")
    



# --- Bug Risk Agent: Get PR Diffs and File Content ---
def get_diff_for_pr(repo, pr_number: int):
    try:
        pr = repo.get_pull(pr_number)
        files = pr.get_files()

        diff_data = {}
        for file in files:
            filename = file.filename
            patch = file.patch
            try:
                content = repo.get_contents(filename, ref=pr.head.ref).decoded_content.decode()
            except Exception as e:
                content = f"Error reading content: {e}"

            diff_data[filename] = {
                "patch": patch,
                "full_content": content
            }

        return diff_data
    except GithubException as e:
        raise Exception(f"Error fetching PR #{pr_number}: {e}")

# --- Codebase Review Agent: Get Full Codebase ---
def get_full_codebase(owner: str, repo: str, branch: str = "main") -> str:
    """Fetches repository structure and contents using GitHub API. Works for public and private repos."""
    try:
        load_dotenv()
        access_token = os.getenv("GITHUB_TOKEN")  # Optional for public repos

        # If access_token is not set, use unauthenticated access (rate-limited)
        g = Github(access_token) if access_token else Github()
        
        try:
            repo_obj = g.get_repo(f"{owner}/{repo}")
        except UnknownObjectException:
            raise ValueError(f"Repository {owner}/{repo} not found. Please check the owner and repo name.")

        # Try to get the specified branch, fallback to default branch if not found
        try:
            branch_ref = repo_obj.get_branch(branch)
        except:
            default_branch = repo_obj.default_branch
            branch = default_branch
            branch_ref = repo_obj.get_branch(default_branch)

        tree = repo_obj.get_git_tree(sha=branch_ref.commit.sha, recursive=True).tree

        repo_structure = "Repository Structure:\n"
        for file in tree:
            repo_structure += f"{file.path}\n"
        
        loader = GithubFileLoader(
            repo=f"{owner}/{repo}",
            access_token=access_token,  # Can be None for public repos
            branch=branch,
            github_api_url="https://api.github.com",
            file_filter=lambda file_path: file_path.endswith(('.py', '.md', '.txt')),
        )
        
        documents = loader.load()
        repo_contents = "\nRepository Contents:\n"
        for doc in documents:
            repo_contents += f"\nFile: {doc.metadata['source']}\n{doc.page_content}\n{'-'*80}\n"
        
        return repo_structure + repo_contents

    except Exception as e:
        raise Exception(f"Error fetching repository: {str(e)}")
# --- Agent Input Providers ---
def get_bug_risk_agent_inputs(repo_full_name: str, pr_number: int):
    repo_owner, repo_name = repo_full_name.split("/")
    diff_data = fetch_pr_diff(repo_owner, repo_name, pr_number)
    return json.dumps(diff_data, ensure_ascii=False, indent=2)

def get_codebase_review_agent_inputs(repo_full_name: str, branch="main"):
    owner, repo = repo_full_name.split("/")
    return get_full_codebase(owner, repo, branch)

def get_pr_conversation_agent_inputs(repo_full_name: str, pr_number: int):
    repo_owner, repo_name = repo_full_name.split("/")
    comments = fetch_pr_conversation(repo_owner, repo_name, pr_number)
    return json.dumps(comments, ensure_ascii=False, indent=2)

# --- Main Function ---
def main():
    # Configure this for your test case
    repo_full_name = "python/cpython"
    repo_owner = "python"
    repo_name = "cpython"
    pr_number = 135057
    branch = "main"

    # print("\n--- Bug Risk Agent Inputs ---")
    # try:
    #     bug_inputs=get_bug_risk_agent_inputs(repo_full_name, pr_number)
    #     print(bug_inputs) 
    # except Exception as e:
    #     print(f"Error: {e}")

    # print("\n--- Codebase Review Agent Inputs ---")
    # try:
    #      codebase_inputs = get_codebase_review_agent_inputs(repo_full_name, branch)
    #      print(codebase_inputs)
    # except Exception as e:
    #     print(f"Error: {e}")

    print("\n--- Conversatons---")
    try:
         comments = get_pr_conversation_agent_inputs(repo_full_name,pr_number)
        #  print(comments)
         with open("conversations_agent_output.json", "w", encoding="utf-8") as f:
            f.write(comments)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()