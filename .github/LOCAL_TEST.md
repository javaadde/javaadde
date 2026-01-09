# Test GitHub Stats Update Locally

This script allows you to test the stats update locally before pushing to GitHub.

## Prerequisites

Install required Python packages:

```bash
pip install PyGithub requests
```

## Generate a GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name like "README Stats"
4. Select scopes: `public_repo` (or just `repo` if you want private repo stats too)
5. Click "Generate token"
6. Copy the token (you won't see it again!)

## Run the Test

### On Windows (PowerShell):

```powershell
$env:GITHUB_TOKEN="your_token_here"
$env:USERNAME="javaadde"
python .github/scripts/update_stats.py
```

### On Linux/Mac:

```bash
export GITHUB_TOKEN="your_token_here"
export USERNAME="javaadde"
python .github/scripts/update_stats.py
```

## What to Expect

The script will:
1. Fetch your GitHub stats using the API
2. Format them into a nice table
3. Update the `### 📊 GitHub Stats` section in README.md
4. Print success messages

Check your README.md to see the updated stats!

## Note

⚠️ **Don't commit your personal access token!** 

The token is only needed for local testing. When the workflow runs on GitHub Actions, it automatically uses the built-in `GITHUB_TOKEN` secret.
