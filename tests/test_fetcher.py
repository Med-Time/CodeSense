import requests
from unittest.mock import patch
from core.fetcher import fetch_pr_diff

@patch("requests.get")
def test_fetch_pr_diff_success(mock_get):
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = [{
        "filename": "app.py",
        "patch": "@@ -1 +1 @@\n-print('Hello')\n+print('Hi')"
    }]

    token = "dummy"
    result = fetch_pr_diff("owner", "repo", 1, token)

    assert len(result) == 1
    assert result[0]["file"] == "app.py"
    assert "added" in result[0]
    assert "removed" in result[0]
