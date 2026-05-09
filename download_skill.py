import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


OWNER = "black-yt"
REPO = "skills"
REF = "main"
API_BASE = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN")


def github_json(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "skills-download-skill",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    req = Request(
        url,
        headers=headers,
    )
    with urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def github_bytes(url):
    headers = {"User-Agent": "skills-download-skill"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    req = Request(url, headers=headers)
    with urlopen(req) as response:
        return response.read()


def download_dir(repo_path, output_dir, overwrite=False):
    url = f"{API_BASE}/repos/{OWNER}/{REPO}/contents/{repo_path}?ref={REF}"
    items = github_json(url)
    if isinstance(items, dict):
        items = [items]

    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    for item in items:
        item_type = item.get("type")
        item_path = item["path"]
        name = item["name"]

        if item_type == "dir":
            count += download_dir(item_path, output_dir / name, overwrite=overwrite)
            continue

        if item_type != "file":
            print(f"[skip] {item_type}: {item_path}")
            continue

        target = output_dir / name
        if target.exists() and not overwrite:
            print(f"[skip] exists: {target}")
            continue

        data = github_bytes(item["download_url"])
        tmp = target.with_suffix(target.suffix + ".tmp")
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, target)
        print(f"[download] {target}")
        count += 1

    return count


def main():
    parser = argparse.ArgumentParser(description="Download one skill folder from black-yt/skills.")
    parser.add_argument("skill_name", help="Skill folder name, for example: docx_splitting")
    parser.add_argument(
        "-o",
        "--output-dir",
        default=None,
        help="Output directory. Defaults to ./<skill_name>.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")
    args = parser.parse_args()

    skill_name = args.skill_name.strip("/ ")
    if not skill_name or "/" in skill_name or "\\" in skill_name:
        print("error: skill_name must be a single folder name, for example: docx_splitting", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir) if args.output_dir else Path(skill_name)

    try:
        count = download_dir(skill_name, output_dir, overwrite=args.overwrite)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if exc.code == 404:
            print(f"error: skill not found: {skill_name}", file=sys.stderr)
        elif exc.code == 403 and "rate limit" in detail.lower():
            print("error: GitHub API rate limit exceeded. Set GITHUB_TOKEN and retry.", file=sys.stderr)
        else:
            print(f"error: GitHub API error {exc.code}: {detail}", file=sys.stderr)
        sys.exit(1)
    except URLError as exc:
        print(f"error: network error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"done: {count} file(s)")


if __name__ == "__main__":
    main()
