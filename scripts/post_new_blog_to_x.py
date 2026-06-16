#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path("/home/dazeb/projects/dennysentinel.com")
BLOG_DIR = ROOT / "src" / "content" / "blog"
STATE_FILE = ROOT / ".cache" / "x-blog-post-state.json"
BASE_URL = os.environ.get("DENNYSENTINEL_BASE_URL", "https://dennysentinel.com")
XURL = os.environ.get("XURL_BIN", "xurl")


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def git(args: list[str]) -> str:
    return run(["git", "-C", str(ROOT), *args]).stdout.strip()


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}
    fm = parts[1].strip().splitlines()
    data = {}
    for line in fm:
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        data[k.strip()] = v.strip().strip('"')
    body = parts[2].strip()
    data["body"] = body
    return data


def summarize(data: dict) -> str:
    title = data.get("title") or "New blog post"
    desc = data.get("description") or ""
    body = data.get("body", "")
    lead = desc or re.sub(r"\s+", " ", body[:240]).strip()
    lead = re.sub(r"\s+", " ", lead).strip()
    if len(lead) > 180:
        lead = lead[:177].rstrip() + "..."
    return title, lead


def build_post(title: str, desc: str, url: str) -> str:
    parts = [f"New on Dennysentinel: {title}"]
    if desc:
        parts.append(desc)
    parts.append(url)
    text = "\n\n".join(parts)
    max_len = 2500
    if len(text) <= max_len:
        return text
    budget = max_len - len(url) - 4
    head = f"New on Dennysentinel: {title}"
    remaining = max(0, budget - len(head))
    desc = desc[:remaining].rstrip()
    if desc.endswith("..."):
        pass
    elif len(desc) == remaining and remaining > 0:
        desc = desc[:-3].rstrip() + "..." if remaining > 3 else desc[:remaining]
    return f"{head}\n\n{desc}\n\n{url}"[:max_len]


def build_image_path(hero_image: str | None, slug: str | None = None) -> Path | None:
    if hero_image:
        candidate = ROOT / "public" / hero_image.lstrip("/")
        if candidate.exists():
            return candidate
    if slug:
        for ext in ("jpg", "jpeg", "png", "webp", "avif"):
            candidate = ROOT / "public" / f"{slug}.{ext}"
            if candidate.exists():
                return candidate
    return None


def ensure_frontmatter_hero_image(path: Path, slug: str, hero_image: str | None) -> str | None:
    if hero_image:
        return hero_image
    candidate = build_image_path(None, slug)
    if not candidate:
        return None
    rel = f"/{candidate.name}"
    text = path.read_text(encoding="utf-8")
    if "heroImage:" in text:
        return rel
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return rel
    frontmatter = parts[1].rstrip()
    updated = f"---\n{frontmatter}\nheroImage: \"{rel}\"\n---\n{parts[2].lstrip()}"
    path.write_text(updated, encoding="utf-8")
    return rel


def main() -> int:
    state = load_state()
    last_seen = state.get("last_seen_commit") or ""
    current = git(["rev-parse", "HEAD"])

    if last_seen == current:
        return 0

    if not last_seen:
        state["last_seen_commit"] = current
        state["initialized_at"] = current
        save_state(state)
        return 0

    diff = git(["diff", "--name-only", f"{last_seen}..{current}", "--", "src/content/blog"])
    new_posts = [ROOT / p for p in diff.splitlines() if p.endswith(".md") and (ROOT / p).exists()]
    if not new_posts:
        state["last_seen_commit"] = current
        save_state(state)
        return 0

    posted = []
    for path in new_posts:
        slug = path.stem
        meta = parse_frontmatter(path)
        title, desc = summarize(meta)
        url = f"{BASE_URL.rstrip('/')}/blog/{slug}/"
        message = build_post(title, desc, url)
        hero_image = ensure_frontmatter_hero_image(path, slug, meta.get("heroImage"))
        image_path = build_image_path(hero_image, slug)
        if image_path:
            message = build_post(title, desc, url)
        result = run([XURL, "post", message], check=True)
        posted.append({"file": str(path), "url": url, "stdout": result.stdout.strip(), "image": str(image_path) if image_path else None})

    state["last_seen_commit"] = current
    state["last_posted"] = posted[-1]["url"]
    save_state(state)

    print(json.dumps({"posted": posted}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
