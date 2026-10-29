#!/usr/bin/env python3
"""SDD audit log: every prompt you type and every action Claude takes, in one place for all projects.

Hooks (stdin = the hook's JSON event):
  audit.py hook-prompt     UserPromptSubmit: log the prompt (secrets masked), project, branch, /sdd: step
  audit.py hook-tool       PostToolUse: log the tool and its target (file, command, skill), never contents
  audit.py hook-start      SessionStart: log it, and tell the user where they were last time

Reading (used by /sdd:log):
  audit.py where                       where you are now and what you were doing
  audit.py show [--days N] [--project P] [--feature F] [--grep TEXT] [--tools] [--limit N]

Log: $SDD_AUDIT_DIR or ~/.claude/sdd-audit/audit-YYYY-MM.jsonl. Python 3 stdlib only.
A hook never fails the session: any error is swallowed.
"""
import datetime
import glob
import json
import os
import re
import subprocess
import sys

LOG_DIR = os.environ.get("SDD_AUDIT_DIR") or os.path.join(os.path.expanduser("~"), ".claude", "sdd-audit")
MAX_PROMPT = 4000
SECRETS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[aws-key]"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"), "[github-token]"),
    (re.compile(r"sk-[A-Za-z0-9_-]{20,}"), "[api-key]"),
    (re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "[jwt]"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), "[private-key]"),
    (re.compile(r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key)\b(\s*[:=]\s*)\S+"), r"\1\2[masked]"),
]
SDD_CMD = re.compile(r"^\s*/(sdd(?:-[a-z]+)?):([a-z-]+)\b\s*(.*)", re.S)


def now():
    return datetime.datetime.now().astimezone()


def mask(text):
    for rx, repl in SECRETS:
        text = rx.sub(repl, text)
    return text


def git_info(cwd):
    """(project, branch) for a folder: the git top-level folder name and branch, or the folder name."""
    def run(*args):
        try:
            return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=3).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return ""
    top = run("rev-parse", "--show-toplevel")
    # symbolic-ref also names the branch of a repo with no commits yet; a detached HEAD gets its short sha
    branch = (run("symbolic-ref", "--short", "-q", "HEAD") or run("rev-parse", "--short", "HEAD")) if top else ""
    return os.path.basename(top or cwd.rstrip("/")) or cwd, branch


def log_path(when=None):
    return os.path.join(LOG_DIR, f"audit-{(when or now()):%Y-%m}.jsonl")


def write(entry):
    os.makedirs(LOG_DIR, mode=0o700, exist_ok=True)
    entry = {"ts": now().isoformat(timespec="seconds"), **entry}
    with open(log_path(), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_all(days=None):
    cutoff = now() - datetime.timedelta(days=days) if days else None
    out = []
    for path in sorted(glob.glob(os.path.join(LOG_DIR, "audit-*.jsonl"))):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if cutoff and datetime.datetime.fromisoformat(e["ts"]) < cutoff:
                    continue
                out.append(e)
    return out


def ago(ts):
    secs = int((now() - datetime.datetime.fromisoformat(ts)).total_seconds())
    for unit, size in (("d", 86400), ("h", 3600), ("m", 60)):
        if secs >= size:
            return f"{secs // size}{unit} ago"
    return "just now"


# ---------------------------------------------------------------- hooks

def hook_prompt(ev):
    cwd = ev.get("cwd") or os.getcwd()
    project, branch = git_info(cwd)
    prompt = ev.get("prompt") or ""
    entry = {"event": "prompt", "session": (ev.get("session_id") or "")[:8], "cwd": cwd,
             "project": project, "branch": branch, "prompt": mask(prompt)[:MAX_PROMPT]}
    m = SDD_CMD.match(prompt)
    if m:
        entry["command"] = f"/{m.group(1)}:{m.group(2)}"
        arg = m.group(3).split()
        if arg and re.fullmatch(r"[a-z0-9][a-z0-9-]*", arg[0]):
            entry["feature"] = arg[0]
    write(entry)


def target_of(tool, ti):
    if not isinstance(ti, dict):
        return ""
    for key in ("file_path", "notebook_path", "path"):
        if ti.get(key):
            return str(ti[key])
    for key in ("command", "skill", "url", "pattern", "query", "subagent_type", "description"):
        if ti.get(key):
            return mask(str(ti[key]))[:200]
    return ""


def hook_tool(ev):
    tool = ev.get("tool_name") or ""
    write({"event": "tool", "session": (ev.get("session_id") or "")[:8], "cwd": ev.get("cwd") or "",
           "tool": tool, "target": target_of(tool, ev.get("tool_input"))})


def last_place():
    prompts = [e for e in read_all(days=60) if e.get("event") == "prompt"]
    if not prompts:
        return None, None
    step = next((e for e in reversed(prompts) if e.get("command")), None)
    return prompts[-1], step


def hook_start(ev):
    cwd = ev.get("cwd") or os.getcwd()
    project, branch = git_info(cwd)
    last, step = last_place()          # read before logging this start
    write({"event": "session", "session": (ev.get("session_id") or "")[:8], "cwd": cwd,
           "project": project, "branch": branch, "source": ev.get("source") or ""})
    if not last or (ev.get("source") not in (None, "", "startup", "resume")):
        return
    where = f"{last['project']}" + (f" ({last['branch']})" if last.get("branch") else "")
    msg = f"📍 Last time ({ago(last['ts'])}): {where}"
    if step:
        msg += f" · last SDD step: {step['command']}" + (f" {step['feature']}" if step.get("feature") else "") + f" ({ago(step['ts'])})"
    msg += " · /sdd:log for more"
    print(json.dumps({"systemMessage": msg}))


# ---------------------------------------------------------------- reading

def docs_root(cwd):
    for cand in [cwd] + sorted(glob.glob(os.path.join(cwd, "*"))):
        if os.path.isfile(os.path.join(cand, "specs", "README.md")):
            return cand
    return None


def cmd_where():
    cwd = os.getcwd()
    project, branch = git_info(cwd)
    print(f"## Where you are now\n\n- Folder: `{cwd}`\n- Project: **{project}**" + (f" · branch `{branch}`" if branch else ""))
    repos = [d for d in sorted(glob.glob(os.path.join(cwd, "*"))) if os.path.isdir(os.path.join(d, ".git"))]
    if repos:
        print("- Repos here:")
        for d in repos:
            _, b = git_info(d)
            print(f"  - `{os.path.basename(d)}` on `{b}`")
    entries = read_all(days=60)
    prompts = [e for e in entries if e.get("event") == "prompt"]
    steps = {}
    for e in prompts:
        if e.get("command"):
            steps[e.get("feature") or "(no feature)"] = e
    print("\n## Your SDD work, by feature (last 60 days)\n")
    if steps:
        print("| Feature | Last step | When | Project |\n|---|---|---|---|")
        for feat, e in sorted(steps.items(), key=lambda kv: kv[1]["ts"], reverse=True):
            print(f"| {feat} | `{e['command']}` | {ago(e['ts'])} | {e['project']} |")
    else:
        print("No `/sdd:` commands logged yet.")
    root = docs_root(cwd)
    tool = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills", "trace", "scripts", "sddtool.py")
    if root and os.path.isfile(tool):
        print(f"\n## Spec status (`{os.path.relpath(root, cwd) if root != cwd else '.'}`)\n")
        try:
            print(subprocess.run([sys.executable, "-I", tool, "status", root], capture_output=True,
                                 text=True, timeout=30).stdout.strip())
        except (OSError, subprocess.SubprocessError):
            print("(couldn't run sddtool status)")
    print("\n## Your last prompts\n")
    for e in prompts[-8:]:
        text = " ".join(e["prompt"].split())
        print(f"- {ago(e['ts'])} · {e['project']}: {text[:140]}{'…' if len(text) > 140 else ''}")
    if not prompts:
        print("Nothing logged yet.")


def cmd_show(args):
    def opt(name, default=None, cast=str):
        if name in args:
            i = args.index(name)
            if i + 1 < len(args):
                return cast(args[i + 1])
        return default
    days, limit = opt("--days", 1, int), opt("--limit", 50, int)
    project, feature, grep = opt("--project"), opt("--feature"), opt("--grep")
    tools = "--tools" in args
    rows = []
    for e in read_all(days=days):
        if e.get("event") == "tool" and not tools:
            continue
        if e.get("event") == "session":
            continue
        if project and e.get("project") != project and project not in (e.get("cwd") or ""):
            continue
        if feature and e.get("feature") != feature:
            continue
        text = e.get("prompt") or f"{e.get('tool')} {e.get('target', '')}"
        if grep and grep.lower() not in text.lower():
            continue
        rows.append((e, text))
    print(f"| Time | Project | {'What' if tools else 'Prompt'} |\n|---|---|---|")
    for e, text in rows[-limit:]:
        when = datetime.datetime.fromisoformat(e["ts"]).strftime("%m-%d %H:%M")
        proj = e.get("project") or os.path.basename(e.get("cwd") or "")
        kind = "↳ " if e.get("event") == "tool" else ""
        text = " ".join(text.split()).replace("|", "\\|")
        print(f"| {when} | {proj} | {kind}{text[:200]}{'…' if len(text) > 200 else ''} |")
    print(f"\n{len(rows)} entries (showing the last {min(len(rows), limit)}). Log: `{LOG_DIR}`")


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd.startswith("hook-"):
        try:
            ev = json.load(sys.stdin)
            {"hook-prompt": hook_prompt, "hook-tool": hook_tool, "hook-start": hook_start}[cmd](ev)
        except Exception:      # a logging problem must never block the user
            pass
        return 0
    if cmd == "where":
        cmd_where()
        return 0
    if cmd == "show":
        cmd_show(argv[2:])
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
