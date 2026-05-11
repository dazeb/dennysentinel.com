#!/usr/bin/env python3
"""
Denny Sentinel Blog Post Creator

Creates a new markdown blog post in src/content/blog/ with proper frontmatter,
builds the site, commits, and pushes. Designed to be called by the Hermes agent
for automated publishing.

Usage:
  python3 scripts/new-post.py --title "My Post Title" --desc "Short description" [--hero hero-image.jpg]

Environment variables (optional):
  GIT_COMMIT=1         Auto-commit the new post
  GIT_PUSH=1           Auto-push (implies GIT_COMMIT)
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone

BLOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "content", "blog")


def slugify(title: str) -> str:
    """Convert a title to a URL-friendly slug."""
    slug = title.lower()
    for ch in " _,":
        slug = slug.replace(ch, "-")
    for ch in "!?.:;\"'()[]{}":
        slug = slug.replace(ch, "")
    slug = slug.strip("-")
    slug = "-".join(filter(None, slug.split("-")))
    return slug


def create_post(title: str, description: str, body_file: str | None, hero: str | None) -> tuple[str, str]:
    """Create a new blog post file and return (filepath, slug)."""
    slug = slugify(title)
    now = datetime.now(timezone.utc)

    frontmatter_lines = [
        "---",
        f'title: "{title}"',
        f'description: "{description}"',
        f"pubDate: '{now.strftime('%b %d %Y')}'",
    ]
    if hero:
        frontmatter_lines.append(f'heroImage: "/{hero.lstrip("/")}"')
    frontmatter_lines.append("---")
    frontmatter_lines.append("")

    body = ""
    if body_file:
        with open(body_file) as f:
            body = f.read()

    content = "\n".join(frontmatter_lines) + body

    os.makedirs(BLOG_DIR, exist_ok=True)
    filepath = os.path.join(BLOG_DIR, f"{slug}.md")
    with open(filepath, "w") as f:
        f.write(content)

    return filepath, slug


def main():
    parser = argparse.ArgumentParser(description="Create a new Denny Sentinel blog post")
    parser.add_argument("--title", "-t", required=True, help="Post title")
    parser.add_argument("--desc", "-d", required=True, help="Short description")
    parser.add_argument("--body", "-b", help="File with post body content (optional)")
    parser.add_argument("--hero", help="Hero image path relative to public/ (optional)")
    parser.add_argument(
        "--push", "-p", action="store_true", default=False, help="Commit and push (auto-builds)"
    )
    parser.add_argument(
        "--no-build", action="store_true", default=False, help="Skip build step"
    )
    args = parser.parse_args()

    filepath, slug = create_post(args.title, args.desc, args.body, args.hero)
    print(f"Created: {filepath}")
    print(f"Slug: {slug}")
    print(f"URL: https://dennysentinel.com/blog/{slug}/")

    should_push = args.push or os.environ.get("GIT_PUSH") == "1"
    should_commit = should_push or os.environ.get("GIT_COMMIT") == "1"

    if not should_commit:
        print("\nTo commit: GIT_COMMIT=1 python3 scripts/new-post.py ...")
        print("To push:   GIT_PUSH=1 python3 scripts/new-post.py ...")
        return

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Build
    if not args.no_build:
        print("\nBuilding site...")
        result = subprocess.run(["npm", "run", "build"], cwd=repo_root, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Build failed:\n{result.stderr}", file=sys.stderr)
            sys.exit(1)
        print(result.stdout.split("\n")[-3:])

    # Git commit
    result = subprocess.run(
        ["git", "add", filepath, "dist/"],
        cwd=repo_root, capture_output=True, text=True
    )
    result = subprocess.run(
        ["git", "commit", "-m", f"blog: {args.title}", "--", filepath, "dist/"],
        cwd=repo_root, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Commit failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"\nCommitted: {result.stdout.strip()}")

    if should_push:
        result = subprocess.run(
            ["git", "push"], cwd=repo_root, capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"Push failed:\n{result.stderr}", file=sys.stderr)
            sys.exit(1)
        print(f"Pushed: {result.stdout.strip()}")


if __name__ == "__main__":
    main()
