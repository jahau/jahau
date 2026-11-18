"""Validate Markdown structure and links in profile README files.

Usage: python scripts/check_readme.py [--offline] README.md [...]

Checks:
- every row of a Markdown table has the same number of columns as its header
- relative links point to files that exist in the repository
- external http(s) links and images respond with a non-error status
- GitHub badges from img.shields.io (`/github/<kind>/<owner>/<repo>`) refer
  to a repository that exists, since shields.io renders an image even for
  missing repositories

`--offline` skips network checks. Exit status is 1 when any check fails.
"""

import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

USER_AGENT = "profile-readme-link-check/1.0"
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HTML_LINK = re.compile(r"""\b(?:href|src)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
SHIELDS_GITHUB = re.compile(r"^https://img\.shields\.io/github/[\w-]+(?:/[\w-]+)*?/([\w.-]+)/([\w.-]+?)(?:\?.*)?$")


def table_errors(path: Path, lines: list[str]) -> list[str]:
    errors, header_columns = [], None
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            header_columns = None
            continue
        columns = len(re.split(r"(?<!\\)\|", stripped)) - 2
        if header_columns is None:
            header_columns = columns
        elif columns != header_columns:
            errors.append(f"{path}:{number}: table row has {columns} columns, header has {header_columns}")
    return errors


def fetch_status(url: str) -> tuple[int | None, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.status, ""
        except urllib.error.HTTPError as error:
            if error.code == 429 and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            return error.code, ""
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            if attempt < 2:
                time.sleep(2)
                continue
            return None, str(error)
    return None, "retries exhausted"


def link_errors(path: Path, text: str, offline: bool) -> list[str]:
    errors, seen = [], set()
    line_of = {}
    for number, line in enumerate(text.splitlines(), start=1):
        for pattern in (MARKDOWN_LINK, HTML_LINK):
            for match in pattern.finditer(line):
                line_of.setdefault(match.group(1), number)

    for url, number in line_of.items():
        where = f"{path}:{number}"
        if url.startswith("#") or url.startswith("mailto:"):
            continue
        if not url.startswith(("http://", "https://")):
            target = (path.parent / url.split("#")[0]).resolve()
            if not target.exists():
                errors.append(f"{where}: relative link target does not exist: {url}")
            continue
        if url.startswith("http://"):
            errors.append(f"{where}: use https instead of http: {url}")
        if offline:
            continue

        checks = [url]
        badge = SHIELDS_GITHUB.match(url)
        if badge:
            checks.append(f"https://github.com/{badge.group(1)}/{badge.group(2)}")
        for check in checks:
            if check in seen:
                continue
            seen.add(check)
            status, reason = fetch_status(check)
            if status is None:
                errors.append(f"{where}: request failed for {check}: {reason}")
            elif status == 429:
                print(f"warning: {where}: rate limited, not verified: {check}", file=sys.stderr)
            elif status >= 400:
                label = "badge repository" if check != url else "link"
                errors.append(f"{where}: {label} returned HTTP {status}: {check}")
    return errors


def main(arguments: list[str]) -> int:
    offline = "--offline" in arguments
    paths = [Path(argument) for argument in arguments if argument != "--offline"]
    if not paths:
        print(__doc__, file=sys.stderr)
        return 2
    errors = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        errors += table_errors(path, text.splitlines())
        errors += link_errors(path, text, offline)
    for error in errors:
        print(error, file=sys.stderr)
    print(f"Checked {len(paths)} file(s): {len(errors)} problem(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
