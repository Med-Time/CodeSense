import re
import requests
from utils.chunker import chunk_diff
import tempfile
import subprocess

def clone_repo_temp(git_url):
    temp_dir = tempfile.mkdtemp()
    subprocess.run(["git", "clone", git_url, temp_dir], check=True)
    return temp_dir


GITHUB_API = "https://api.github.com"

def parse_github_pr_url(pr_url):
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

def fetch_pr_diff(repo_owner="", repo_name="", pr_number=1, token="", pr_url=None):
    if pr_url:
        repo_owner, repo_name, pr_number = parse_github_pr_url(pr_url)
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"{GITHUB_API}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
    # url = f"{GITHUB_API}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/commits"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    files = response.json()
    print(files)

    parsed_changes = []

    for file in files:
        filename = file["filename"]
        patch = file.get("patch")
        print(f"{filename} with {patch}")

        if patch:
            added_chunks, removed_chunks = chunk_diff(patch)

            parsed_changes.append({
                "file": filename,
                "added": added_chunks,
                "removed": removed_chunks
            })

    return parsed_changes

def load_repo_code(git_url):
    repo_dir = clone_repo_temp(git_url)
    all_code = read_all_files(repo_dir)
    return structure_for_agents(all_code)
