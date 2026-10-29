#!/usr/bin/env python3
"""PreToolUse hook (Bash): in web-ui, block installing a package that has no Approved row
in the team's Package Requests sheet, and tell Claude to file the request (TEAM-RULES.md §7).

Reads the hook JSON on stdin. Prints a PreToolUse decision, or nothing to let the call through.
Python 3 stdlib only.
"""
import csv
import io
import json
import os
import shlex
import sys
import urllib.request

SHEET_CSV = ("https://docs.google.com/spreadsheets/d/16uJc2NUiDNs2TibBV1LMlVpkDdA5u65NxYen4Lo43Ew"
             "/export?format=csv&gid=438764700")
# subcommands that add or upgrade a named package, per package manager
INSTALL_CMDS = {
    "pnpm": {"add", "install", "i", "update", "up", "upgrade"},
    "npm": {"install", "i", "add", "isntall", "update", "up", "upgrade"},
    "yarn": {"add", "upgrade", "up"},
    "bun": {"add", "install", "i", "update"},
}
VALUE_FLAGS = {"--filter", "-F", "--dir", "-C", "--workspace", "--prefix", "--registry", "--tag", "--cwd"}
SEPARATORS = {"&&", "||", ";", "|", "&"}


def decide(decision, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


def package_name(spec):
    """'@scope/name@^1.2' -> '@scope/name', 'name@1' -> 'name'; None for paths, URLs, git specs."""
    if spec.startswith((".", "/", "~")) or ":" in spec:
        return None
    at = spec.find("@", 1)
    return (spec[:at] if at > 0 else spec).lower() or None


def installs(command, cwd):
    """Yield (dir, [package names]) for every install of named packages in a shell command."""
    try:
        lex = shlex.shlex(command, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        return
    here, words = cwd, []
    for tok in tokens + [";"]:
        if tok not in SEPARATORS:
            words.append(tok)
            continue
        if words and words[0] == "cd" and len(words) > 1:
            here = os.path.normpath(os.path.join(here, os.path.expanduser(words[1])))
        elif words and os.path.basename(words[0]) in INSTALL_CMDS:
            pm, rest = os.path.basename(words[0]), words[1:]
            sub_i = next((i for i, w in enumerate(rest) if not w.startswith("-")
                          and (i == 0 or rest[i - 1] not in VALUE_FLAGS)), None)
            if sub_i is not None and rest[sub_i] in INSTALL_CMDS[pm]:
                names, skip = [], False
                for w in rest[sub_i + 1:]:
                    if skip:
                        skip = False
                    elif w in VALUE_FLAGS:
                        skip = True
                    elif not w.startswith("-"):
                        name = package_name(w)
                        if name:
                            names.append(name)
                if names:
                    yield here, names
        words = []


def is_web_ui(path):
    """True when the nearest package.json above `path` depends on next (web-ui)."""
    path = os.path.abspath(path)
    while True:
        pj = os.path.join(path, "package.json")
        if os.path.isfile(pj):
            try:
                with open(pj, encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, ValueError):
                return False
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            return "next" in deps
        parent = os.path.dirname(path)
        if parent == path:
            return False
        path = parent


def sheet_rows():
    if os.environ.get("SDD_PACKAGE_SHEET_FILE"):  # tests
        with open(os.environ["SDD_PACKAGE_SHEET_FILE"], encoding="utf-8") as f:
            return list(csv.reader(f))
    with urllib.request.urlopen(SHEET_CSV, timeout=10) as r:
        return list(csv.reader(io.StringIO(r.read().decode("utf-8"))))


def lookup(rows, name):
    """(row number, status) of the newest request for `name`, or None."""
    found = None
    for n, r in enumerate(rows, 1):
        if n < 6 or len(r) < 11:
            continue
        cells = [c.strip().lower() for c in (r[3], r[5])]
        if cells[0] == name or any(name in c.replace("pnpm add", " ").split() for c in cells):
            found = (n, r[10].strip() or "no status yet")
    return found


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    if data.get("tool_name") != "Bash":
        return
    command = (data.get("tool_input") or {}).get("command", "")
    cwd = data.get("cwd") or os.getcwd()
    wanted = sorted({n for d, names in installs(command, cwd) if is_web_ui(d) for n in names})
    if not wanted:
        return
    try:
        rows = sheet_rows()
    except Exception as e:  # network, auth, parse — let the user decide
        decide("ask", f"Couldn't read the team's Package Requests sheet ({e}), so the approval of "
                      f"{', '.join(wanted)} can't be checked. Install only if you know it's Approved.")
    missing, pending = [], []
    for name in wanted:
        hit = lookup(rows, name)
        if hit is None:
            missing.append(name)
        elif hit[1].lower() != "approved":
            pending.append(f"{name} (row {hit[0]}: {hit[1]})")
    if not missing and not pending:
        return
    parts = ["Blocked: web-ui packages need an Approved package request (TEAM-RULES.md §7) before they're installed."]
    if missing:
        parts.append(f"No request yet for: {', '.join(missing)}. Don't install. Follow the sdd:manage-dependencies "
                     "skill §1–§4 now: check it's needed, draft the request, and file it in the Package Requests "
                     "sheet with Requested By = the team member using Claude (from git config user.email, §4.2).")
    if pending:
        parts.append(f"Requested but not approved: {', '.join(pending)}. Don't file it again; tell the user it's "
                     "waiting for the approver and ask how to go on without it.")
    decide("deny", " ".join(parts))


if __name__ == "__main__":
    main()
