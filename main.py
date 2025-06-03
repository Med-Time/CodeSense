from utils.fetcher import fetch_pr_diff
import os
from utils.chunker import chunk_diff
import json

pr_url = "https://github.com/jasmcaus/opencv-course/pull/26"


print("Fetching PR diff...")
fetched_diff = fetch_pr_diff(pr_url=pr_url)
print("Fetched PR diff successfully.")
with open("fetched_diff.json", "w", encoding="utf-8") as f:
    json.dump(fetched_diff, f, ensure_ascii=False, indent=2)
print("Saved fetched diff to fetched_diff.json.")
