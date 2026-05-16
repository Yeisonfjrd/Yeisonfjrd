import requests
import re
from datetime import datetime, timezone, timedelta

ARG_TZ = timezone(timedelta(hours=-3))
today = datetime.now(ARG_TZ).strftime("%B %d, %Y")

def get_quote():
    try:
        res = requests.get(
            "https://api.quotable.io/quotes/random?tags=technology,science",
            timeout=5
        )
        data = res.json()[0]
        return f'> "{data["content"]}" — **{data["author"]}**'
    except:
        return '> "First, solve the problem. Then, write the code." — **John Johnson**'

def get_recent_activity(username="yeisonfjrd"):
    try:
        res = requests.get(
            f"https://api.github.com/users/{username}/events/public",
            timeout=5
        )
        events = res.json()
        lines = []
        seen = set()

        for event in events[:20]:
            repo = event["repo"]["name"]
            etype = event["type"]

            if etype == "PushEvent" and repo not in seen:
                msg = event["payload"]["commits"][-1]["message"].split("\n")[0]
                lines.append(f"- 🔨 Pushed to **{repo}**: `{msg}`")
                seen.add(repo)
            elif etype == "CreateEvent" and repo not in seen:
                lines.append(f"- ✨ Created **{repo}**")
                seen.add(repo)
            elif etype == "WatchEvent" and repo not in seen:
                lines.append(f"- ⭐ Starred **{repo}**")
                seen.add(repo)

            if len(lines) >= 5:
                break

        return "\n".join(lines) if lines else "- No recent public activity"
    except:
        return "- Could not load activity"

quote = get_quote()
activity = get_recent_activity()

dynamic_block = f"""<!-- DYNAMIC_START -->
<div align="center">

### 💬 Quote of the day
{quote}

</div>

### 🕐 Recent Activity
{activity}

*Last updated: {today}*

<!-- DYNAMIC_END -->"""
with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()
if "<!-- DYNAMIC_START -->" in content:
    content = re.sub(
        r"<!-- DYNAMIC_START -->.*?<!-- DYNAMIC_END -->",
        dynamic_block,
        content,
        flags=re.DOTALL
    )
else:
    content += "\n\n" + dynamic_block

with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)

print("README updated successfully!")
