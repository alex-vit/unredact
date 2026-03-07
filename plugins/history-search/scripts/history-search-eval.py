#!/usr/bin/env python3
"""Evaluate history-search.py with challenging semantic queries.

These queries are deliberately hard for keyword-based tools (grep, rg, fzf).
They use natural language, synonyms, conceptual descriptions, and indirect references
that semantic search should handle but BM25/FTS would struggle with.
"""

import io
import json
import os
import subprocess
import sys
import time

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SCRIPT = os.path.expanduser("~/.claude/scripts/history-search.py")

# Each query has: (query, expected_signal, notes)
# expected_signal: keyword/concept that SHOULD appear in good results
QUERIES = [
    # --- Conceptual / synonym-heavy ---
    ("when the app icon disappeared from the taskbar",
     "systray|tray|icon", "No exact keyword match for 'taskbar disappeared'"),

    ("that session where we dealt with Android certificate expiry",
     "signing|key|rotation|certificate", "Conceptual: certificate expiry ≈ key rotation"),

    ("debugging why the Windows installer silently failed",
     "inno|installer|setup|silent", "Synonym: 'silently failed' vs actual error terms"),

    ("working on the Windows Go desktop app with hotkeys",
     "hotkey|shortcut|keyboard|monibright|plop", "Paraphrase: 'desktop app hotkeys' ≈ monibright/plop"),

    # --- Indirect / conversational references ---
    ("figuring out how to package a Go app with an installer",
     "inno|installer|setup|exe|msi|wix", "Paraphrase: 'package with installer' ≈ Inno Setup"),

    ("session about making Claude remember things across conversations",
     "memory|skill|plugin|CLAUDE.md|session", "Meta: searching for search-about-memory"),

    # --- Problem descriptions (no jargon) ---
    ("the screen brightness kept jumping around unexpectedly",
     "brightness|monitor|flicker|refresh", "No jargon, just symptoms"),

    ("refactoring how we organize Claude Code skills and notes",
     "skill|notes|CLAUDE.md|plugin|organize|refactor", "Meta: reorganizing Claude Code config"),

    ("that annoying issue where tests passed locally but failed in CI",
     "ci|circle|test|flaky|pass", "Classic dev complaint, no specific terms"),

    # --- Technical but paraphrased ---
    ("how to store and retrieve secrets securely in the pipeline",
     "secret|gsm|gcp|vault|op|credential|1password", "Paraphrase: secrets management ≈ GSM/1Password/op"),

    ("writing a script to sync files between machines",
     "sync|rsync|backup|copy", "Generic description of specific tooling"),

    ("the Play Store upload and release process",
     "play|store|aab|release|upload|bundle", "Paraphrase of Android release flow"),

    # --- Cross-project discovery ---
    ("all the times we worked on system tray apps",
     "systray|tray|energye|monibright|plop", "Should find across monibright/plop"),

    ("sessions about creating or improving Claude Code plugins",
     "plugin|skill|claude-plugin|SKILL.md", "Should find plugin development sessions"),

    # --- Temporal / vague ---
    ("that recent session about Gradle build configuration",
     "gradle|build.gradle|android|signing", "Vague temporal + topic"),

    ("when we discussed inter-African payment networks",
     "gimac|payment|africa|currency", "Niche domain topic"),
]


def run_query(query, n=5):
    """Run history-search.py and return (results_text, elapsed_seconds)."""
    start = time.time()
    result = subprocess.run(
        [sys.executable, SCRIPT, query, "-n", str(n)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    elapsed = time.time() - start
    output = result.stdout + result.stderr
    return output.strip(), elapsed


def score_result(output, expected_signal):
    """Check if any expected signal keywords appear in the output."""
    signals = expected_signal.lower().split("|")
    output_lower = output.lower()
    found = [s for s in signals if s in output_lower]
    return len(found), len(signals), found


def main():
    print(f"Running {len(QUERIES)} evaluation queries...\n")
    print("=" * 80)

    total_hit = 0
    total_miss = 0
    total_time = 0
    details = []

    for i, (query, expected, notes) in enumerate(QUERIES, 1):
        output, elapsed = run_query(query)
        total_time += elapsed
        hits, total_signals, found = score_result(output, expected)
        hit = hits > 0

        status = "HIT" if hit else "MISS"
        if hit:
            total_hit += 1
        else:
            total_miss += 1

        # Extract scores from output
        import re
        scores = re.findall(r'\[(\d+\.\d+)\]', output)
        top_score = scores[0] if scores else "—"
        n_results = len(re.findall(r'^--- \[', output, re.MULTILINE))

        print(f"\n[{i:2d}] {status}  top={top_score}  n={n_results}  {elapsed:.1f}s")
        print(f"     Q: {query}")
        print(f"     Expect: {expected}")
        print(f"     Found: {', '.join(found) if found else '(none)'}")
        if not hit:
            # Show first result excerpt for debugging
            lines = output.split("\n")
            preview = " | ".join(l.strip() for l in lines[:3] if l.strip())[:120]
            print(f"     Got: {preview}")

        details.append({
            "query": query, "hit": hit, "top_score": top_score,
            "n_results": n_results, "elapsed": elapsed,
            "found_signals": found, "notes": notes,
        })

    print("\n" + "=" * 80)
    print(f"\nSUMMARY: {total_hit}/{len(QUERIES)} hits, {total_miss} misses")
    print(f"Total time: {total_time:.1f}s, avg: {total_time/len(QUERIES):.1f}s per query")

    if total_miss > 0:
        print(f"\nMISSED QUERIES:")
        for d in details:
            if not d["hit"]:
                print(f"  - {d['query']}")
                print(f"    ({d['notes']})")


if __name__ == "__main__":
    main()
