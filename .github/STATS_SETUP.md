# GitHub Stats Auto-Update Setup

This repository uses GitHub Actions to automatically update the README with fresh GitHub statistics daily.

## 🚀 How It Works

1. **Daily Schedule**: The workflow runs every day at 00:00 UTC (5:30 AM IST)
2. **Fetches Stats**: Uses GitHub API to get your latest stats (repos, stars, forks, followers, top languages)
3. **Updates README**: Automatically updates the `### 📊 GitHub Stats` section
4. **Commits Changes**: Pushes the updated README back to the repository

## 📁 Files Created

- `.github/workflows/update-stats.yml` - GitHub Actions workflow configuration
- `.github/scripts/update_stats.py` - Python script that fetches and formats stats

## ⚙️ Setup Instructions

### 1. Push to GitHub

First, commit and push all the files to your GitHub repository:

```bash
git add .
git commit -m "Add GitHub stats auto-update workflow"
git push origin main
```

### 2. Enable GitHub Actions

1. Go to your repository on GitHub
2. Click on the **Actions** tab
3. If prompted, click **"I understand my workflows, go ahead and enable them"**

### 3. Manual Trigger (Optional)

To test the workflow immediately without waiting for the daily schedule:

1. Go to **Actions** tab in your repository
2. Click on **"Update GitHub Stats"** workflow
3. Click **"Run workflow"** button
4. Select the branch (usually `main`)
5. Click **"Run workflow"**

The workflow will run and update your README within a minute!

## 🔧 Customization

### Change Update Frequency

Edit `.github/workflows/update-stats.yml` and modify the cron schedule:

```yaml
schedule:
  - cron: '0 0 * * *'  # Daily at midnight UTC
  # Examples:
  # - cron: '0 */12 * * *'  # Every 12 hours
  # - cron: '0 0 * * 1'     # Every Monday
```

### Modify Stats Display

Edit `.github/scripts/update_stats.py` to customize:
- Which stats to display
- Formatting and styling
- Number of top languages shown (currently 5)

## 🎯 What Gets Updated

- 📦 Public Repositories count
- ⭐ Total Stars Earned
- 🍴 Total Forks
- 👥 Followers count
- 📝 Public Gists count
- 🔥 Top 5 Programming Languages
- 🕐 Last updated timestamp

## 🐛 Troubleshooting

### Workflow Not Running?

1. Check if GitHub Actions is enabled in your repository settings
2. Verify the workflow file is in `.github/workflows/` directory
3. Check the Actions tab for any error messages

### Stats Not Updating?

1. Go to Actions tab and check the latest workflow run
2. Click on the failed run to see error logs
3. Ensure the Python script has correct permissions

## 📝 Notes

- The workflow uses `GITHUB_TOKEN` which is automatically provided by GitHub Actions
- No additional secrets or tokens need to be configured
- The commit message includes `[skip ci]` to prevent infinite workflow loops
- Stats are fetched only from public repositories

## 🎉 That's It!

Your GitHub stats will now update automatically every day! 🚀
