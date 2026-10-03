import requests
import re
from datetime import datetime, timezone, timedelta

ARG_TZ = timezone(timedelta(hours=-3))
today = datetime.now(ARG_TZ).strftime("%d/%m/%Y")


def get_recent_activity(username="yeisonfjrd"):
    try:
        res = requests.get(
            f"https://api.github.com/users/{username}/events/public",
            headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "readme-bot"},
            timeout=10,
        )
        if res.status_code != 200:
            return "_No recent public activity._"

        ICONS = {
            "PushEvent": "🔨",
            "CreateEvent": "✨",
            "WatchEvent": "⭐",
            "ForkEvent": "🍴",
            "PullRequestEvent": "🔀",
            "IssuesEvent": "🐛",
        }

        lines, seen = [], set()

        for event in res.json()[:30]:
            etype = event.get("type", "")
            repo = event["repo"]["name"]
            if repo in seen or etype not in ICONS:
                continue

            icon = ICONS[etype]

            if etype == "PushEvent":
                commits = event.get("payload", {}).get("commits", [])
                if not commits:
                    continue
                msg = commits[-1]["message"].split("\n")[0][:55]
                lines.append(f"| {icon} | [{repo}](https://github.com/{repo}) | `{msg}` |")
            elif etype == "CreateEvent":
                ref = event.get("payload", {}).get("ref_type", "repository")
                lines.append(f"| {icon} | [{repo}](https://github.com/{repo}) | Created {ref} |")
            elif etype == "WatchEvent":
                lines.append(f"| {icon} | [{repo}](https://github.com/{repo}) | Starred |")
            elif etype == "ForkEvent":
                lines.append(f"| {icon} | [{repo}](https://github.com/{repo}) | Forked |")
            elif etype == "PullRequestEvent":
                action = event.get("payload", {}).get("action", "opened")
                lines.append(f"| {icon} | [{repo}](https://github.com/{repo}) | {action.capitalize()} a PR |")

            seen.add(repo)
            if len(lines) >= 5:
                break

        if not lines:
            return "_No recent public activity._"

        return "| | Repository | Activity |\n|:---:|:---|:---|\n" + "\n".join(lines)

    except Exception:
        return "_No recent public activity._"


activity = get_recent_activity()

dynamic_block = f"""<!-- DYNAMIC_START -->
{activity}

<sub>Updated automatically · {today}</sub>
<!-- DYNAMIC_END -->"""

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

if "<!-- DYNAMIC_START -->" in content:
    content = re.sub(
        r"<!-- DYNAMIC_START -->.*?<!-- DYNAMIC_END -->",
        dynamic_block,
        content,
        flags=re.DOTALL,
    )
else:
    content = content.rstrip() + "\n\n" + dynamic_block + "\n"

with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)

print(f"README actualizado — {today}")
