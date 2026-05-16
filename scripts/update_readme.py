import requests
import re
import random
from datetime import datetime, timezone, timedelta

ARG_TZ = timezone(timedelta(hours=-3))
today = datetime.now(ARG_TZ).strftime("%d/%m/%Y")

FRASES = [
    ("Primero, resolvé el problema. Después, escribí el código.", "John Johnson"),
    ("El código es como el humor: si hay que explicarlo, es malo.", "Cory House"),
    ("La simplicidad es el alma de la eficiencia.", "Austin Freeman"),
    ("Cualquier tonto puede escribir código que una computadora entiende. Los buenos programadores escriben código que los humanos entienden.", "Martin Fowler"),
    ("Siempre programá como si el tipo que va a mantener tu código fuera un asesino violento que sabe dónde vivís.", "John Woods"),
    ("El debugging es dos veces más difícil que escribir el código. Por eso, si escribís el código lo más inteligente posible, sos por definición no suficientemente listo para debuggearlo.", "Brian Kernighan"),
    ("Los programas deben escribirse para que los lean las personas, y de paso, para que los ejecuten las máquinas.", "Harold Abelson"),
    ("Primero hacelo funcionar, después hacelo rápido.", "Kent Beck"),
    ("El código limpio siempre parece que fue escrito por alguien que se importa.", "Robert C. Martin"),
    ("La experiencia es el nombre que la gente le da a sus errores.", "Oscar Wilde"),
    ("El software es una gran combinación entre arte e ingeniería.", "Bill Gates"),
    ("Aprender a programar es la habilidad más valiosa que podés adquirir en el siglo XXI.", "Marc Andreessen"),
    ("La programación no se trata de lo que sabés; se trata de lo que podés descubrir.", "Chris Pine"),
    ("Medir el progreso del desarrollo de software por líneas de código es como medir el avance de la construcción de un avión por el peso.", "Bill Gates"),
    ("Un buen programador es alguien que siempre mira en ambas direcciones antes de cruzar una calle de un solo sentido.", "Doug Linder"),
    ("El mejor error que podés tener es el que aparece en producción. Ahí sí aprendés.", "Anónimo"),
    ("No se trata de tener ideas; se trata de hacer que las ideas sucedan.", "Scott Belsky"),
    ("Escribe código como si la persona que lo va a mantener fuera un psicópata que sabe dónde vivís.", "Martin Golding"),
    ("Los buenos programadores no solo resuelven problemas. Los buenos programadores crean soluciones que otros puedan entender.", "Anónimo"),
    ("En teoría, teoría y práctica son lo mismo. En la práctica, no lo son.", "Yogi Berra"),
]

def get_quote():
    frase, autor = random.choice(FRASES)
    return f'> *"{frase}"*\n>\n> — **{autor}**'

def get_recent_activity(username="yeisonfjrd"):
    try:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "readme-bot",
        }
        res = requests.get(
            f"https://api.github.com/users/{username}/events/public",
            headers=headers,
            timeout=10,
        )
        if res.status_code != 200:
            return "_Sin actividad pública reciente._"

        events = res.json()
        lines = []
        seen = set()

        ICONS = {
            "PushEvent": "🔨",
            "CreateEvent": "✨",
            "WatchEvent": "⭐",
            "ForkEvent": "🍴",
            "PullRequestEvent": "🔀",
            "IssuesEvent": "🐛",
        }

        for event in events[:30]:
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
                ref_type = event.get("payload", {}).get("ref_type", "repositorio")
                lines.append(f"| {icon} | [{repo}](https://github.com/{repo}) | Creó {ref_type} |")

            elif etype == "WatchEvent":
                lines.append(f"| {icon} | [{repo}](https://github.com/{repo}) | Le dio una estrella |")

            elif etype == "ForkEvent":
                lines.append(f"| {icon} | [{repo}](https://github.com/{repo}) | Hizo fork |")

            elif etype == "PullRequestEvent":
                action = event.get("payload", {}).get("action", "abrió")
                lines.append(f"| {icon} | [{repo}](https://github.com/{repo}) | {action.capitalize()} un PR |")

            seen.add(repo)
            if len(lines) >= 5:
                break

        if not lines:
            return "_Sin actividad pública reciente._"

        table = "| | Repositorio | Acción |\n|:---:|:---|:---|\n"
        table += "\n".join(lines)
        return table

    except Exception:
        return "_Sin actividad pública reciente._"


quote = get_quote()
activity = get_recent_activity()

dynamic_block = f"""<!-- DYNAMIC_START -->

---

### 💬 Frase del día

{quote}

---

### 🕐 Actividad reciente

{activity}

<sub>Actualizado automáticamente · {today}</sub>

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
