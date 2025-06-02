import os
from dotenv import load_dotenv
from github import Github
from github.GithubException import UnknownObjectException
from langchain_community.document_loaders import GithubFileLoader
import sys

def fetch_repo(owner: str, repo: str, branch: str = "main") -> str:
    """Fetches repository structure and contents using GitHub API. Works for public and private repos."""
    try:
        load_dotenv()
        access_token = os.getenv("GITHUB_TOKEN")  # Optional for public repos

        # If access_token is not set, use unauthenticated access (rate-limited)
        g = Github(access_token) if access_token else Github()
        
        try:
            repo_obj = g.get_repo(f"{owner}/{repo}")
            print(f"Using repository: {repo_obj}")
        except UnknownObjectException:
            raise ValueError(f"Repository {owner}/{repo} not found. Please check the owner and repo name.")

        # Try to get the specified branch, fallback to default branch if not found
        try:
            branch_ref = repo_obj.get_branch(branch)
            print(f"Using branch: {branch_ref}")
        except:
            default_branch = repo_obj.default_branch
            print(f"Branch '{branch}' not found, using default branch: {default_branch}")
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
        print(f"Loaded {tree} tree from the repository.")
        print(f"Loaded {documents} documents from the repository.")
        repo_contents = "\nRepository Contents:\n"
        for doc in documents:
            repo_contents += f"\nFile: {doc.metadata['source']}\n{doc.page_content}\n{'-'*80}\n"
        
        return repo_structure + repo_contents

    except Exception as e:
        raise Exception(f"Error fetching repository: {str(e)}")

def main():
    print("GitHub Repository Fetcher")
    print("-" * 30)
    
    # Example usage with default values anmol52490/RAG
    owner = input("Enter GitHub owner/org: ").strip() or "anmol52490"
    repo = input("Enter repository name: ").strip() or "Gen-email"
    branch = input("Enter branch (default: main): ").strip() or "main"
    output_file = input("Enter output filename (default: repo_output.txt): ").strip() or "repo_output.txt"

    try:
        print(f"\nFetching repository {owner}/{repo} ({branch} branch)...")
        result = fetch_repo(owner, repo, branch)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\nSuccess! Repository data saved to {output_file}")
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()