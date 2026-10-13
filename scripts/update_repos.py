"""Rellena la sección de proyectos del README con los repos públicos ordenados por fecha de creación.

Se ejecuta desde .github/workflows/update-readme.yml. En local:
    GITHUB_TOKEN=$(gh auth token) python scripts/update_repos.py
"""
import json
import os
import re
import urllib.request
from datetime import datetime
from pathlib import Path

USER = "Zer0Dev-exe"
README = Path(__file__).resolve().parent.parent / "README.md"
START, END = "<!-- REPOS:START -->", "<!-- REPOS:END -->"


def fetch_repos():
    repos, page = [], 1
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    while True:
        url = f"https://api.github.com/users/{USER}/repos?type=owner&per_page=100&page={page}"
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as r:
            batch = json.load(r)
        if not batch:
            return repos
        repos += batch
        page += 1


def cell(text):
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def render(repos):
    repos = [r for r in repos if not r["fork"] and not r["archived"] and r["name"] != USER]
    repos.sort(key=lambda r: r["created_at"], reverse=True)
    rows = ["| Proyecto | Descripción | Lenguaje | Creado |", "|---|---|---|---|"]
    for r in repos:
        created = datetime.strptime(r["created_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y")
        rows.append(f"| [{r['name']}]({r['html_url']}) | {cell(r['description'])} "
                    f"| {r['language'] or '—'} | {created} |")
    return "\n".join(rows)


def main():
    text = README.read_text(encoding="utf-8")
    block = f"{START}\n{render(fetch_repos())}\n{END}"
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    if new != text:
        README.write_text(new, encoding="utf-8", newline="\n")
        print("README actualizado")
    else:
        print("Sin cambios")


if __name__ == "__main__":
    main()
