#!/usr/bin/env python3
"""Search Claude Code session history using semantic embeddings via llm similar."""

import argparse
import io
import json
import os
import subprocess
import sys
from pathlib import Path

# Force UTF-8 output on Windows (cp1252 can't handle unicode in session excerpts)
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

LLM_CLI = os.path.expanduser("~/.local/bin/llm")
PROJECTS_DIR = Path.home() / ".claude" / "projects"
COLLECTION = "sessions"


def run_similar(query: str, count: int) -> list[dict]:
    """Run llm similar and return parsed results."""
    cmd = [LLM_CLI, "similar", COLLECTION, "-c", query, "-n", str(count)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running llm similar: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    results = []
    for line in result.stdout.strip().splitlines():
        if line.strip():
            results.append(json.loads(line))
    return results


def id_to_path(entry_id: str) -> Path:
    """Map embedding ID to JSONL file path."""
    # ID format: -Users-alex-code-wave\UUID.jsonl (relative to projects dir)
    # On Windows the ID uses backslash as separator within the path
    return PROJECTS_DIR / entry_id


def extract_project(entry_id: str) -> str:
    """Extract project name from embedding ID."""
    # ID: -Users-alex-code-wave\UUID.jsonl → first component is project dir
    parts = entry_id.replace("\\", "/").split("/")
    project_dir = parts[0] if parts else "unknown"
    # Project dir is like -Users-alex-code-wave → extract last segment
    segments = project_dir.split("-")
    # Find the meaningful name: last non-empty segment
    return segments[-1] if segments else project_dir


def _extract_text(content) -> str:
    """Extract plain text from a message content field (string or block list)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return " ".join(parts)
    return ""


def extract_session_info(filepath: Path) -> tuple[str, str]:
    """Read JSONL file and extract date and best user message excerpt.

    Scans the first several user messages and picks the most informative one
    (longest non-trivial message), since short first prompts like "do X" are
    less useful than richer follow-up context.
    """
    date = "unknown"
    candidates: list[str] = []
    max_user_msgs = 5

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Extract timestamp for date
                if date == "unknown":
                    ts = msg.get("timestamp")
                    if ts:
                        date = ts[:10]

                msg_type = msg.get("type")
                if msg_type == "user":
                    text = _extract_text(msg.get("message", {}).get("content", ""))
                    if text:
                        candidates.append(text)
                        if len(candidates) >= max_user_msgs:
                            break
                elif msg_type == "queue-operation" and msg.get("operation") == "enqueue":
                    text = msg.get("content", "")
                    if text:
                        candidates.append(text)
    except (OSError, IOError) as e:
        return date, f"(unable to read file: {e})"

    if not candidates:
        return date, ""

    # Pick the most informative candidate: prefer longer messages, but use
    # the first one if all are similar length (it has the most context)
    best = candidates[0]
    for c in candidates[1:]:
        if len(c) > len(best) * 1.5:
            best = c
    return date, best[:800].strip()


def is_agent_session(filepath: Path) -> bool:
    """Check if a session file is a subagent (Task tool) session."""
    return filepath.stem.startswith("agent-")


def main():
    parser = argparse.ArgumentParser(
        description="Search Claude Code session history using semantic embeddings"
    )
    parser.add_argument("query", help="Search query (natural language)")
    parser.add_argument(
        "-n", "--count", type=int, default=10, help="Number of results (default: 10)"
    )
    parser.add_argument(
        "--project", help="Filter results to a specific project name"
    )
    parser.add_argument(
        "--min-score", type=float, default=0.15,
        help="Minimum similarity score to show (default: 0.15)"
    )
    args = parser.parse_args()

    # Fetch extra results to compensate for filtering and deduplication
    fetch_count = args.count * 4
    results = run_similar(args.query, fetch_count)

    printed = 0
    seen_excerpts: set[str] = set()
    for entry in results:
        if printed >= args.count:
            break

        entry_id = entry["id"]
        score = entry["score"]
        if score < args.min_score:
            break  # Results are sorted by score; rest will be lower
        project = extract_project(entry_id)

        if args.project and args.project.lower() != project.lower():
            continue

        filepath = id_to_path(entry_id)
        if not filepath.exists():
            continue

        date, excerpt = extract_session_info(filepath)

        # Deduplicate by excerpt (retried/queued sessions share the same prompt)
        dedup_key = excerpt[:200]
        if dedup_key in seen_excerpts:
            continue
        seen_excerpts.add(dedup_key)

        # Extract UUID (truncated to 8 chars) from filename
        uuid_short = filepath.stem[:8]
        agent_tag = " agent" if is_agent_session(filepath) else ""

        print(f"--- [{project}] {date} ({uuid_short}) [{score:.2f}]{agent_tag} ---")
        print(excerpt)
        print()
        printed += 1

    if printed == 0:
        print("No results found.", file=sys.stderr)


if __name__ == "__main__":
    main()
