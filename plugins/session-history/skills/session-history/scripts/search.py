#!/usr/bin/env python3
"""Search Claude Code session history for keywords and context.

Scans JSONL session files in ~/.claude/projects/ and extracts matching
conversations. Uses case-insensitive word matching with scoring based
on how many query terms appear and how densely they cluster.

Usage:
    python3 search.py "keyword" [options]

Options:
    --project NAME       Filter to sessions from projects matching NAME
    --max N              Maximum results to return (default: 5)
    --show               Show message snippets (not just file paths)
    --past               Exclude current session
    --exclude-id ID      Explicitly exclude a session ID
    --after DATE         Only sessions modified after DATE (YYYY-MM-DD)
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


PROJECTS_DIR = Path.home() / ".claude" / "projects"

# Message types worth searching
SEARCHABLE_TYPES = {"user", "assistant"}


@dataclass
class MessageRecord:
    """A single message extracted from a session."""
    role: str
    text: str
    timestamp: str
    git_branch: str


@dataclass
class Match:
    """A matching snippet from a session."""
    file: Path
    project: str
    session_id: str
    timestamp: str
    role: str
    text: str
    score: float = 0.0
    git_branch: str = ""


def extract_text(record: dict) -> str:
    """Extract readable text from a session record, skipping noise."""
    msg = record.get("message", {})
    if not isinstance(msg, dict):
        return ""
    content = msg.get("content", "")

    if isinstance(content, str):
        # Skip system/meta content
        for prefix in ("<local-command", "<command-name>", "<system-reminder>"):
            if content.startswith(prefix):
                return ""
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type", "")
            if item_type == "text":
                text = item.get("text", "")
                # Strip system reminders embedded in text blocks
                if "<system-reminder>" in text:
                    text = re.sub(
                        r"<system-reminder>.*?</system-reminder>",
                        "", text, flags=re.DOTALL,
                    ).strip()
                if text and not text.startswith("<local-command"):
                    parts.append(text)
            # Skip tool_use, tool_result, thinking -- too noisy for search
        return "\n".join(parts)

    return ""


def load_session_messages(path: Path) -> list[MessageRecord]:
    """Load a session file and extract searchable messages."""
    messages = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if record.get("type") not in SEARCHABLE_TYPES:
                    continue
                if record.get("isMeta"):
                    continue

                text = extract_text(record)
                if not text.strip():
                    continue

                messages.append(MessageRecord(
                    role=record.get("type", ""),
                    text=text,
                    timestamp=record.get("timestamp", ""),
                    git_branch=record.get("gitBranch", ""),
                ))
    except OSError:
        pass
    return messages


def score_text(query_words: list[str], text: str) -> float:
    """Score how well text matches query words.

    Returns 0 if no match. Higher scores = better match.
    Scoring rewards:
    - More query words present (primary signal)
    - Exact phrase match (bonus)
    - Shorter text with all terms (density bonus)
    """
    text_lower = text.lower()
    matched = sum(1 for w in query_words if w in text_lower)
    if matched == 0:
        return 0.0

    # Base score: fraction of query words found
    base = matched / len(query_words)

    # Exact phrase bonus
    query_phrase = " ".join(query_words)
    phrase_bonus = 0.5 if query_phrase in text_lower else 0.0

    # Density bonus: shorter texts with all terms are more relevant
    density = matched / (len(text_lower.split()) + 1) * 10
    density_bonus = min(density, 0.3)

    return base + phrase_bonus + density_bonus


def find_sessions(
    project_filter: Optional[str] = None,
    exclude_session: Optional[str] = None,
    after_date: Optional[str] = None,
) -> list[Path]:
    """Find all session JSONL files, optionally filtered."""
    if not PROJECTS_DIR.exists():
        return []

    after_ts = 0.0
    if after_date:
        try:
            after_ts = datetime.strptime(after_date, "%Y-%m-%d").timestamp()
        except ValueError:
            pass

    files = []
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue

        if project_filter:
            if project_filter.lower() not in project_dir.name.lower():
                continue

        for jsonl_file in project_dir.glob("*.jsonl"):
            if exclude_session and jsonl_file.stem == exclude_session:
                continue
            if after_ts and jsonl_file.stat().st_mtime < after_ts:
                continue
            files.append(jsonl_file)

    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return files


def format_project_name(dirname: str) -> str:
    """Convert project dir name to readable form.

    -Users-alex-code-wave -> wave
    -Users-alex-code-wave-android -> wave/android
    """
    parts = dirname.strip("-").split("-")
    # Find "code" and take everything after it
    try:
        code_idx = parts.index("code")
        relevant = parts[code_idx + 1:]
        return "/".join(relevant) if relevant else dirname
    except ValueError:
        return parts[-1] if parts else dirname


def truncate_around_match(text: str, query_words: list[str], max_len: int = 400) -> str:
    """Show text around the best matching region."""
    if len(text) <= max_len:
        return text

    text_lower = text.lower()
    # Find the first occurrence of any query word
    best_pos = len(text)
    for w in query_words:
        pos = text_lower.find(w)
        if pos >= 0 and pos < best_pos:
            best_pos = pos

    if best_pos == len(text):
        best_pos = 0

    # Center the window around the match
    half = max_len // 2
    start = max(0, best_pos - half)
    end = min(len(text), start + max_len)
    start = max(0, end - max_len)

    snippet = text[start:end]

    # Break at word boundaries
    if start > 0:
        first_space = snippet.find(" ")
        if first_space > 0 and first_space < 30:
            snippet = snippet[first_space + 1:]
        snippet = "..." + snippet
    if end < len(text):
        last_space = snippet.rfind(" ")
        if last_space > len(snippet) - 30:
            snippet = snippet[:last_space]
        snippet = snippet + "..."

    return snippet


def main():
    parser = argparse.ArgumentParser(description="Search Claude Code session history")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--project", help="Filter by project name")
    parser.add_argument("--max", type=int, default=5, help="Max results (default: 5)")
    parser.add_argument("--show", action="store_true", help="Show message snippets")
    parser.add_argument("--past", action="store_true", help="Exclude current session")
    parser.add_argument("--exclude-id", help="Explicitly exclude a session ID")
    parser.add_argument("--after", help="Only sessions after YYYY-MM-DD")
    args = parser.parse_args()

    exclude_session = args.exclude_id
    if args.past and not exclude_session:
        exclude_session = os.environ.get("CLAUDE_SESSION_ID")

    files = find_sessions(
        project_filter=args.project,
        exclude_session=exclude_session,
        after_date=args.after,
    )

    if len(files) == 0:
        print("No session files found.", file=sys.stderr)
        sys.exit(1)

    query_words = args.query.lower().split()
    all_matches: list[Match] = []
    session_match_counts: dict[str, int] = {}

    for session_file in files:
        messages = load_session_messages(session_file)
        if len(messages) == 0:
            continue

        project = format_project_name(session_file.parent.name)
        session_id = session_file.stem

        for msg in messages:
            score = score_text(query_words, msg.text)
            if score > 0:
                all_matches.append(Match(
                    file=session_file,
                    project=project,
                    session_id=session_id,
                    timestamp=msg.timestamp,
                    role=msg.role,
                    text=msg.text,
                    score=score,
                    git_branch=msg.git_branch,
                ))
                session_match_counts[session_id] = (
                    session_match_counts.get(session_id, 0) + 1
                )

    # Sort by score descending, then by timestamp descending
    all_matches.sort(key=lambda m: (-m.score, m.timestamp), reverse=False)
    all_matches.sort(key=lambda m: -m.score)

    if len(all_matches) == 0:
        print(f"No matches for '{args.query}'.", file=sys.stderr)
        sys.exit(1)

    if args.show:
        seen = 0
        for match in all_matches:
            if seen >= args.max:
                break
            ts_short = match.timestamp[:10] if match.timestamp else "?"
            branch_info = f" ({match.git_branch})" if match.git_branch else ""
            snippet = truncate_around_match(match.text, query_words)
            print(f"--- [{match.project}] {ts_short}{branch_info} ---")
            print(f"[{match.role}] {snippet}")
            print()
            seen += 1
    else:
        seen_sessions: set[str] = set()
        count = 0
        for match in all_matches:
            if count >= args.max:
                break
            if match.session_id in seen_sessions:
                continue
            seen_sessions.add(match.session_id)
            hits = session_match_counts.get(match.session_id, 0)
            ts_short = match.timestamp[:10] if match.timestamp else "?"
            branch_info = f" ({match.git_branch})" if match.git_branch else ""
            print(f"[{match.project}] {ts_short}{branch_info} - {hits} hits - {match.file}")
            count += 1


if __name__ == "__main__":
    main()
