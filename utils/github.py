import requests
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv

load_dotenv()


def get_user_data(username, access_token):
    user_url = f"https://api.github.com/users/{username}"
    headers = {"Authorization": f"token {access_token}"}
    response = requests.get(user_url, headers=headers)
    if response.status_code == 200:
        print(response.json()["repos_url"])
        return response.json()
    else:
        return {"Error": response.status_code}


def get_all_commits_last_year(username, access_token):
    last_year_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    commits = 0
    events_url = f"https://api.github.com/users/{username}/events"
    headers = {"Authorization": f"token {access_token}"}
    response = requests.get(events_url, headers=headers)
    if response.status_code == 200:
        events = response.json()
        commits_last_year = []
        for event in events:
            if event["type"] == "PushEvent" and event["created_at"] >= last_year_date:
                commits_last_year.extend(event["payload"]["commits"])
                commits += 1
        return commits
    else:
        return {"Error": response.status_code}


def get_all_prs(username, access_token):
    prs = []
    page = 1
    while True:
        prs_url = f"https://api.github.com/users/{username}/events?page={page}"
        headers = {"Authorization": f"token {access_token}"}
        response = requests.get(prs_url, headers=headers)
        if response.status_code == 200:
            events = response.json()
            if not events:  # No more events, stop pagination
                break
            for event in events:
                if event["type"] == "PullRequestEvent":
                    prs.append(event)
            page += 1
        else:
            return {"Error": response.status_code}
            break
    return prs


def get_total_public_repos(username, access_token):
    user_data = get_user_data(username, access_token)
    if user_data:
        return user_data["public_repos"]
    else:
        return None


def get_github_statistics(username, access_token):
    user_data = get_user_data(username, access_token)
    if user_data:
        repos_url = user_data["repos_url"]
        headers = {"Authorization": f"token {access_token}"}
        repos_response = requests.get(repos_url, headers=headers)
        if repos_response.status_code == 200:
            repos = repos_response.json()
            prs = get_all_prs(username, access_token)
            return {
                "name": user_data["name"],
                "followers": user_data["followers"],
                "following": user_data["following"],
                "commits_since_joined": sum(repo["size"] for repo in repos),
                "commits_current_year": get_all_commits_last_year(username, access_token),
                "Language Usage": {lang: round((sum(1 for repo in repos if repo["language"] == lang) / len(repos)) * 100, 2) for lang in set(repo["language"] for repo in repos if repo["language"])},
                "recent_repo": {
                    "repo_name": max(repos, key=lambda x: x["created_at"])["name"],
                    "date_created": max(repos, key=lambda x: x["created_at"])["created_at"],
                    "description": max(repos, key=lambda x: x["created_at"])["description"]
                },
                "stars_earned": sum(repo["stargazers_count"] for repo in repos),
                "pull_requests": len(prs),
                "total_public_repos_created": get_total_public_repos(username, access_token)
            }
        else:
            return {"Error": repos_response.status_code}
    else:
        return None



# Example usage:
username = "nimisha-sara"
access_token = os.getenv("GITHUB_TOKEN")
print(access_token)
statistics = get_github_statistics(username, access_token)
if statistics:
    for key, value in statistics.items():
        print(f"{key}: {value}")
