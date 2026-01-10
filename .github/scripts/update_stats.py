#!/usr/bin/env python3
import os
import re
import requests
from datetime import datetime, timedelta

def get_github_data(username, token):
    """Fetch GitHub data using both REST and GraphQL APIs"""
    headers = {"Authorization": f"token {token}"}
    
    # 1. Fetch REST API data (Repos, Stars, Followers)
    rest_url = f"https://api.github.com/users/{username}"
    user_data = requests.get(rest_url, headers=headers).json()
    
    # 2. Fetch GraphQL API data (Contribution Calendar)
    graphql_url = "https://api.github.com/graphql"
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
        repositories(first: 100, ownerAffiliations: OWNER) {
          nodes {
            stargazerCount
            languages(first: 5, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node {
                  name
                }
              }
            }
          }
        }
      }
    }
    """
    variables = {"login": username}
    response = requests.post(graphql_url, json={"query": query, "variables": variables}, headers=headers)
    gql_data = response.json()
    
    if 'errors' in gql_data:
        print(f"GraphQL Errors: {gql_data['errors']}")
        return None

    user_gql = gql_data['data']['user']
    calendar = user_gql['contributionsCollection']['contributionCalendar']
    
    # Calculate Streak
    all_days = []
    for week in calendar['weeks']:
        for day in week['contributionDays']:
            all_days.append(day)
    
    all_days.sort(key=lambda x: x['date'], reverse=True)
    
    current_streak = 0
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Start checking from today or yesterday
    start_index = 0
    if all_days[0]['date'] != today and all_days[0]['date'] != yesterday:
        current_streak = 0
    else:
        for day in all_days:
            if day['contributionCount'] > 0:
                current_streak += 1
            else:
                # If we hit a 0 and it's not today's pending count, we stop
                if day['date'] != today:
                    break
    
    # Calculate Total Stars
    total_stars = sum(repo['stargazerCount'] for repo in user_gql['repositories']['nodes'])
    
    # Language Stats
    lang_stats = {}
    for repo in user_gql['repositories']['nodes']:
        for lang_edge in repo['languages']['edges']:
            name = lang_edge['node']['name']
            size = lang_edge['size']
            lang_stats[name] = lang_stats.get(name, 0) + size
            
    top_languages = sorted(lang_stats.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        'total_repos': user_data.get('public_repos', 0),
        'followers': user_data.get('followers', 0),
        'total_stars': total_stars,
        'total_contributions': calendar['totalContributions'],
        'current_streak': current_streak,
        'top_languages': [l[0] for l in top_languages],
        'last_updated': datetime.now().strftime('%B %d, %Y')
    }

def format_stats(stats):
    return f"""<!-- START_STATS -->
### 📊 GitHub Real-time Stats

<p align="center">
  <img src="https://img.shields.io/badge/Contribution_Streak-{stats['current_streak']}_Days-orange?style=for-the-badge&logo=github&logoColor=white" />
  <img src="https://img.shields.io/badge/Total_Contributions-{stats['total_contributions']}-blue?style=for-the-badge&logo=github&logoColor=white" />
  <img src="https://img.shields.io/badge/Total_Stars-{stats['total_stars']}-yellow?style=for-the-badge&logo=star&logoColor=black" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Public_Repos-{stats['total_repos']}-green?style=flat-square&logo=git&logoColor=white" />
  <img src="https://img.shields.io/badge/Followers-{stats['followers']}-lightgrey?style=flat-square&logo=github&logoColor=white" />
</p>

<div align="center">
  <sub>Last automated update: {stats['last_updated']} • Built with ⚡ by Javad</sub>
</div>
<!-- END_STATS -->"""

def update_readme(stats_content):
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Robust replacement using comment tags
    pattern = r'<!-- START_STATS -->.*?<!-- END_STATS -->'
    
    # Fallback to the old title-based pattern if tags are not found yet
    if '<!-- START_STATS -->' not in content:
        pattern = r'### 📊 GitHub Stats.*?(?=\n---|\Z)'
    new_content = re.sub(pattern, stats_content, content, flags=re.DOTALL)
    
    with os.fdopen(os.open('README.md', os.O_WRONLY | os.O_TRUNC | os.O_CREAT, 0o644), 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == "__main__":
    TOKEN = os.environ.get('GITHUB_TOKEN')
    USER = os.environ.get('USERNAME', 'javaadde')
    
    if TOKEN:
        data = get_github_data(USER, TOKEN)
        if data:
            update_readme(format_stats(data))
            print("🚀 Stats updated successfully!")
        else:
            print("❌ Failed to fetch data.")
    else:
        print("⚠️ No GITHUB_TOKEN found.")
