import subprocess
from datetime import datetime, timezone
import os
import re

CHANGELOG_PATH = "CHANGELOG.md"


def run_git_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def get_recent_commits(limit=10):
    """
    Fetches the most recent commits formatted as 'hash|author|subject'.
    """
    log_output = run_git_command(f'git log -n {limit} --pretty=format:"%h|%an|%s"')
    if not log_output:
        return []

    commits = []
    for line in log_output.splitlines():
        parts = line.split('|', 2)
        if len(parts) == 3:
            commits.append({
                'hash': parts[0],
                'author': parts[1],
                'subject': parts[2]
            })
    return commits


def categorize_commits(commits):
    categories = {
        'Features': [],
        'Bug Fixes': [],
        'CI/CD & DevOps': [],
        'Security': [],
        'Documentation & Chores': []
    }

    for c in commits:
        subj = c['subject']
        h = c['hash']

        # Skip merge commit notices from changelog list
        if subj.startswith('Merge pull request') or subj.startswith('Merge branch'):
            continue

        item = f"- [`{h}`] {subj}"

        if subj.startswith('feat'):
            categories['Features'].append(item)
        elif subj.startswith('fix'):
            categories['Bug Fixes'].append(item)
        elif subj.startswith('ci') or subj.startswith('cd'):
            categories['CI/CD & DevOps'].append(item)
        elif subj.startswith('sec'):
            categories['Security'].append(item)
        else:
            categories['Documentation & Chores'].append(item)

    return categories


def generate_changelog_entry(version_label=None):
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    current_sha = run_git_command("git rev-parse --short HEAD") or "unknown"
    label = version_label or f"Staging Build ({current_sha})"

    commits = get_recent_commits(limit=15)
    categorized = categorize_commits(commits)

    lines = [
        f"## [{label}] - {now_utc}\n",
        f"**Commit SHA**: `{current_sha}`\n"
    ]

    for category, items in categorized.items():
        if items:
            lines.append(f"### {category}")
            for item in items:
                lines.append(item)
            lines.append("")

    return "\n".join(lines).strip() + "\n\n"


def update_changelog():
    entry = generate_changelog_entry()

    header = "# 📝 Changelog\n\nAll notable changes to the Notes App CI/CD Pipeline are documented here.\n\n"

    if os.path.exists(CHANGELOG_PATH):
        with open(CHANGELOG_PATH, 'r', encoding='utf-8') as f:
            existing = f.read()

        # Remove header if present to avoid duplication
        if existing.startswith("# 📝 Changelog"):
            existing_body = re.sub(r"^# 📝 Changelog.*?\n\n", "", existing, flags=re.DOTALL)
        else:
            existing_body = existing

        new_content = header + entry + existing_body
    else:
        new_content = header + entry

    with open(CHANGELOG_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ Successfully updated {CHANGELOG_PATH}")


if __name__ == '__main__':
    update_changelog()
