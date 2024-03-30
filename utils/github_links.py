def contribution_graph(username: str):
    return f"https://github-readme-activity-graph.vercel.app/graph?username={username}&bg_color=000&point=fff&theme=github-compact"


def streaks_view(username: str):
    return f"https://streak-stats.demolab.com/?user={nimisha-sara}&theme=dark"


def stats(username: str, theme: str = "dark"):
    return f"https://github-readme-stats.vercel.app/api?username={username}&show_icons=true&theme={theme}"


def top_languages(username: str, theme: str = "dark"):
    return f"https://github-readme-stats.vercel.app/api/top-langs/?username={username}&theme={theme}"
