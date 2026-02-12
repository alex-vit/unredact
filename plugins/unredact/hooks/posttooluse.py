#!/usr/bin/env python3
"""PostToolUse hook for unredact plugin.

Outputs a concise one-line summary after each tool call, restoring
per-tool-call visibility that was removed in Claude Code v2.1.20.

Uses systemMessage on stdout (exit 0) to display summaries to the user.
"""

import json
import os
import sys

def is_enabled():
    """Check if unredact is enabled via env var and local config."""
    if os.environ.get("UNREDACT_ENABLED") == "0":
        return False

    # Check per-project config
    config_path = os.path.join(".claude", "unredact.local.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            if not config.get("enabled", True):
                return False
        except (json.JSONDecodeError, IOError, OSError):
            pass

    return True


def basename(path):
    """Extract filename from path."""
    if not path:
        return "?"
    return os.path.basename(path)


def format_read(tool_input, tool_response):
    filename = basename(tool_input.get("file_path", ""))
    n = 0
    if isinstance(tool_response, dict):
        f = tool_response.get("file", {})
        n = f.get("numLines") or f.get("totalLines") or 0
    return f"{filename} \u2014 {n} lines"


def format_grep(tool_input, tool_response):
    pattern = tool_input.get("pattern", "")
    if isinstance(tool_response, dict):
        mode = tool_response.get("mode", "files_with_matches")
        n = tool_response.get("numFiles", 0)
        if mode == "count":
            return f'"{pattern}" \u2014 {n} entries'
        elif mode == "content":
            n = tool_response.get("numLines", n)
            return f'"{pattern}" \u2014 {n} lines'
        else:
            return f'"{pattern}" \u2014 {n} files'
    return f'"{pattern}"'


def format_glob(tool_input, tool_response):
    pattern = tool_input.get("pattern", "")
    n = 0
    if isinstance(tool_response, dict):
        n = tool_response.get("numFiles", len(tool_response.get("filenames", [])))
    return f"{pattern} \u2014 {n} files"


def format_write(tool_input, _tool_response):
    filename = basename(tool_input.get("file_path", ""))
    content = tool_input.get("content", "")
    n = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
    return f"{filename} \u2014 {n} lines"


def format_bash(tool_input, _tool_response):
    desc = tool_input.get("description", "")
    if desc:
        return desc
    cmd = tool_input.get("command", "")
    if len(cmd) > 60:
        cmd = cmd[:60] + "\u2026"
    return cmd


def format_task(tool_input, _tool_response):
    desc = tool_input.get("description", "")
    return desc


def format_notebookedit(tool_input, _tool_response):
    filename = basename(tool_input.get("notebook_path", ""))
    return filename


FORMATTERS = {
    "Read": format_read,
    "Grep": format_grep,
    "Glob": format_glob,
    "Write": format_write,
    "Bash": format_bash,
    "Task": format_task,
    "NotebookEdit": format_notebookedit,
}



def format_tool(tool_name, tool_input, tool_response):
    """Dispatch to the appropriate formatter. Returns None for unknown tools."""
    if tool_name in FORMATTERS:
        return FORMATTERS[tool_name](tool_input, tool_response)
    return None


def main():
    try:
        if not is_enabled():
            sys.exit(0)

        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        tool_response = input_data.get("tool_response", {})

        summary = format_tool(tool_name, tool_input, tool_response)
        if not summary:
            sys.exit(0)

        output = json.dumps({"systemMessage": summary})
        print(output, file=sys.stdout)
        sys.exit(0)

    except Exception:
        # Never crash, never block tool execution
        sys.exit(0)


if __name__ == "__main__":
    main()
