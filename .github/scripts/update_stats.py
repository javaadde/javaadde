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
    
    # Generate Graph
    graph_days = all_days[:10]  # Get last 10 days (reverted order)
    # Sort back to chronological for graphing
    graph_days.sort(key=lambda x: x['date'])
    generate_contribution_graph(graph_days, current_streak)

    return {
        'total_repos': user_data.get('public_repos', 0),
        'followers': user_data.get('followers', 0),
        'total_stars': total_stars,
        'total_contributions': calendar['totalContributions'],
        'current_streak': current_streak,
        'top_languages': [l[0] for l in top_languages],
        'last_updated': datetime.now().strftime('%B %d, %Y')
    }

def generate_contribution_graph(days, streak):
    # Ensure images directory exists
    os.makedirs('images', exist_ok=True)
    
    width = 600
    height = 240
    padding = 30
    
    # Text positioning
    streak_text_y = 35
    
    # Graph positioning
    graph_top_y = 90  # Increased gap
    graph_bottom_y = height - 30 
    graph_height = graph_bottom_y - graph_top_y
    
    bar_width = 20
    gap = (width - (2 * padding)) / len(days)
    
    counts = [d['contributionCount'] for d in days]
    max_val = max(counts) if counts else 0
    if max_val == 0: max_val = 1
    
    def get_bar_height(val):
        h = (val / max_val) * graph_height
        return max(h, 3) if val > 0 else 3 # Min height 3px even for 0 to show presence
    
    svg_content = ""
    
    for i, day in enumerate(days):
        count = day['contributionCount']
        bar_h = get_bar_height(count)
        x = padding + (i * gap) + (gap - bar_width) / 2
        y = graph_bottom_y - bar_h
        
        # Determine color shade based on intensity
        # For 0 contributions, use a very faint gray
        if count == 0:
            opacity = 0.1
        else:
            opacity = 0.5 + (0.5 * (count / max_val))
        
        # Bar
        svg_content += f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_h}" fill="white" fill-opacity="{opacity}" rx="2" />'
        
        # Number (Top of bar)
        text_y = y - 8
        count_text = str(count) if count > 0 else ""
        if count_text:
             svg_content += f'<text x="{x + bar_width/2}" y="{text_y}" text-anchor="middle" class="bar-text">{count_text}</text>'
        
        # Date (Bottom of bar)
        date_str = day.get('date', '')
        if date_str:
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                date_label = dt.strftime('%d %b')
            except:
                date_label = date_str[-5:]
        else:
            date_label = ""
            
        svg_content += f'<text x="{x + bar_width/2}" y="{height - 10}" text-anchor="middle" class="date-text">{date_label}</text>'

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
      <style>
        .header {{ font-family: "Courier New", Courier, monospace; fill: white; font-size: 14px; font-weight: bold; letter-spacing: 1px; }}
        .bar-text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: #ccc; font-size: 12px; }}
        .date-text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: #666; font-size: 10px; }}
        .bg {{ fill: #0d1117; }} 
      </style>
      <rect width="100%" height="100%" class="bg" rx="10"/>
      
      <!-- Streak Text -->
      <text x="{width-padding}" y="{streak_text_y}" text-anchor="end" class="header">Current Streak: {streak} Days</text>
      
      {svg_content}
      
    </svg>"""
    
    with open('images/contribution_graph.svg', 'w') as f:
        f.write(svg)

def format_stats(stats):
    return f"""<!-- START_STATS -->
### 📊 GitHub Real-time Stats

<p align="center">
  <img src="images/contribution_graph.svg" width="100%" alt="Contribution Graph" />
</p>

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
