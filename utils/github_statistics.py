import os
from datetime import datetime, timedelta
import requests


class GitHubStatistics:
    """
    Class to retrieve GitHub statistics for a user
    """

    def __init__(self, username: str, access_token: str):
        """
        Initialize GitHubStatistics with the user's GitHub username and access token

        Args:
            username (str): GitHub username
            access_token (str): GitHub access token
        """
        self.username = username
        self.access_token = access_token

    def _get_user_data(self) -> dict:
        """
        Retrieve data of the GitHub user.

        Returns:
            dict: User data.
        """
        user_url = f"https://api.github.com/users/{self.username}"
        headers = {"Authorization": f"token {self.access_token}"}
        response = requests.get(user_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"Error": response.status_code}

    def _get_all_commits_last_year(self) -> int:
        """
        Retrieve the number of commits made by the user in the last year

        Returns:
            int: Number of commits made in the last year
        """
        last_year_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
        commits = 0
        events_url = f"https://api.github.com/users/{self.username}/events"
        headers = {"Authorization": f"token {self.access_token}"}
        response = requests.get(events_url, headers=headers)
        if response.status_code == 200:
            events = response.json()
            for event in events:
                if event["type"] == "PushEvent" and event["created_at"] >= last_year_date:
                    commits += 1
            return commits
        else:
            return {"Error": response.status_code}

    def _get_all_prs(self) -> list:
        """
        Retrieve information about all pull requests made by the user

        Returns:
            list: List of pull request events
        """
        prs = []
        page = 1
        while True:
            prs_url = f"https://api.github.com/users/{self.username}/events?page={page}"
            headers = {"Authorization": f"token {self.access_token}"}
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

    def _get_total_public_repos(self) -> int:
        """
        Retrieve the total number of public repositories created by the user

        Returns:
            int: Total number of public repositories
        """
        user_data = self._get_user_data()
        if user_data:
            return user_data["public_repos"]
        else:
            return None
    
    def get_contribution_graph(self):
        return f"https://github-readme-activity-graph.vercel.app/graph?username={self.username}&bg_color=000&point=fff&theme=github-compact"

    def _get_github_statistics(self) -> dict:
        """
        Retrieve GitHub statistics for the user

        Returns:
            dict: GitHub statistics
        """
        user_data = self._get_user_data()
        if user_data:
            repos_url = user_data["repos_url"]
            headers = {"Authorization": f"token {self.access_token}"}
            repos_response = requests.get(repos_url, headers=headers)
            if repos_response.status_code == 200:
                repos = repos_response.json()
                prs = self._get_all_prs()
                return {
                    "name": user_data["name"],
                    "followers": user_data["followers"],
                    "following": user_data["following"],
                    "commits_since_joined": sum(repo["size"] for repo in repos),
                    "commits_current_year": self._get_all_commits_last_year(),
                    "Language Usage": {lang: round((sum(1 for repo in repos if repo["language"] == lang) / len(repos)) * 100, 2) for lang in set(repo["language"] for repo in repos if repo["language"])},
                    "recent_repo": {
                        "repo_name": max(repos, key=lambda x: x["created_at"])["name"],
                        "date_created": max(repos, key=lambda x: x["created_at"])["created_at"],
                        "description": max(repos, key=lambda x: x["created_at"])["description"]
                    },
                    "stars_earned": sum(repo["stargazers_count"] for repo in repos),
                    "pull_requests": len(prs),
                    "total_public_repos_created": self._get_total_public_repos()
                }
            else:
                return {"Error": repos_response.status_code}
        else:
            return None

    def get_statistics(self) -> dict:
        """
        Get GitHub statistics for the user

        Returns:
            dict: GitHub statistics
        """
        return self._get_github_statistics()


# Example usage:
if __name__ == "__main__":
    username = "nimisha-sara"
    access_token = os.getenv("GITHUB_TOKEN")
    statistics = GitHubStatistics(username, access_token).get_statistics()
    if statistics:
        for key, value in statistics.items():
            print(f"{key}: {value}")

