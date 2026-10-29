#!/usr/bin/env python3
"""LedgerVision SDD tool: spec/tasks lint, traceability matrix, feature status.

Usage:
  sddtool.py check  <docs-root> <feature>
  sddtool.py trace  <docs-root> <feature> [<repo> ...] [--no-write]
  sddtool.py status <docs-root>

Formats come from <docs-root>/specs/_templates/. Exit: 0 clean, 1 findings, 2 usage error.
Python 3 stdlib only; run with `python3 -I`.
"""
import datetime
import os
import re
import subprocess
import sys

STATUS_RE = re.compile(r"\*\*Status:\*\*\s*(✅|📝|⟳)")
PREFIX_RE = re.compile(r"\*\*Prefix:\*\*\s*`?([A-Z]{2,4})`?")
PLAN_SPEC_RE = re.compile(r"\*\*Spec:\*\*.*?commit\s+`?([0-9a-f]{7,40})`?")
TASK_RE = re.compile(r"^\s*-\s*\[([ xX])\]\s*\*\*(T\d{2,3})\*\*(.*)$")
AFTER_RE = re.compile(r"after\s+((?:T\d{2,3}[,\s]*)+)")
SKIP_DIRS = {".git", "node_modules", "build", "dist", ".next", ".gradle", "target",
             "docs", "venv", ".venv", "__pycache__", "out", "coverage"}
TEST_PATH_RE = re.compile(
    r"(^|/)(src/test|tests?|e2e|__tests__)/|\.(test|spec)\.[cm]?[jt]sx?$|(^|/)test_[^/]*\.py$|_test\.py$")
TEXT_EXT = (".java", ".kt", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py")


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None


def git(root, *args):
    try:
        return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True,
                              timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


class Spec:
    """Parsed spec.md: prefix, status, defined / withdrawn IDs, open questions."""

    def __init__(self, text):
        self.text = text
        m = PREFIX_RE.search(text)
        self.prefix = m.group(1) if m else None
        m = STATUS_RE.search(text)
        self.status = m.group(1) if m else None
        self.defined = {}      # id -> line number of its definition
        self.duplicates = []
        self.withdrawn = set()
        self.open_q = []
        self.malformed = []
        if not self.prefix:
            return
        p = re.escape(self.prefix)
        def_re = re.compile(r"^\s*(?:[-*]|\|)\s*(~~)?\*\*(" + p + r"-[RDEQM]\d{2,3})\*\*(~~)?(.*)$")
        loose_re = re.compile(r"\*\*(" + p + r"-[A-Z]+\d+)\*\*")
        for n, line in enumerate(text.splitlines(), 1):
            m = def_re.match(line)
            if m:
                ident = m.group(2)
                if ident in self.defined:
                    self.duplicates.append((ident, n))
                else:
                    self.defined[ident] = n
                if m.group(1) or "withdrawn" in m.group(4).lower()[:40]:
                    self.withdrawn.add(ident)
                if ident[len(self.prefix) + 1] == "Q" and ident not in self.withdrawn \
                        and not re.search(r"→\s*" + p + r"-D\d+", m.group(4)):
                    self.open_q.append(ident)
                continue
            for lm in loose_re.finditer(line):
                if not re.fullmatch(p + r"-[RDEQM]\d{2,3}", lm.group(1)):
                    self.malformed.append((lm.group(1), n))

    def ids(self, kinds="RE"):
        return sorted(i for i in self.defined if i[len(self.prefix) + 1] in kinds)

    def live(self, kinds="RE"):
        return [i for i in self.ids(kinds) if i not in self.withdrawn]

    def references(self, text):
        return set(re.findall(r"\b" + re.escape(self.prefix) + r"-[RDEQM]\d{2,3}\b", text))


class Tasks:
    def __init__(self, text, prefix):
        self.tasks = {}        # T id -> dict(done, stale, ids, after, line)
        self.duplicates = []
        for n, line in enumerate((text or "").splitlines(), 1):
            m = TASK_RE.match(line)
            if not m:
                continue
            tid, rest = m.group(2), m.group(3)
            if tid in self.tasks:
                self.duplicates.append((tid, n))
                continue
            after = []
            am = AFTER_RE.search(rest)
            if am:
                after = re.findall(r"T\d{2,3}", am.group(1))
            self.tasks[tid] = {
                "done": m.group(1).lower() == "x",
                "stale": "⟳" in rest,
                "ids": set(re.findall(r"\b" + re.escape(prefix) + r"-[RE]\d{2,3}\b", rest)) if prefix else set(),
                "setup": re.search(r"covers:?\s*setup", rest) is not None,
                "after": after,
                "line": n,
            }

    def covering(self, ident):
        return sorted(t for t, v in self.tasks.items() if ident in v["ids"])


def load(docs, feature):
    fdir = os.path.join(docs, "specs", feature)
    text = read(os.path.join(fdir, "spec.md"))
    if text is None:
        die(f"No spec: {fdir}/spec.md")
    spec = Spec(text)
    if not spec.prefix:
        die(f"{feature}: spec.md has no **Prefix:** line")
    plan = read(os.path.join(fdir, "plan.md"))
    tasks_text = read(os.path.join(fdir, "tasks.md"))
    return fdir, spec, plan, Tasks(tasks_text, spec.prefix) if tasks_text is not None else None


def spec_drift(docs, feature, plan):
    """Commits to spec.md after the commit the plan was approved against."""
    if not plan:
        return None, []
    m = PLAN_SPEC_RE.search(plan)
    if not m:
        return None, []
    since = m.group(1)
    log = git(docs, "log", "--oneline", f"{since}..HEAD", "--", f"specs/{feature}/spec.md")
    return since, [l for l in log.splitlines() if l]


# ---------------------------------------------------------------- check

def cmd_check(docs, feature):
    fdir, spec, plan, tasks = load(docs, feature)
    errors, warns = [], []
    p = spec.prefix
    if spec.status is None:
        errors.append("spec.md: no **Status:** (✅ / 📝 / ⟳)")
    for ident, n in spec.duplicates:
        errors.append(f"spec.md:{n}: {ident} defined twice (IDs are never reused)")
    for ident, n in spec.malformed:
        errors.append(f"spec.md:{n}: malformed ID {ident} (expected {p}-R01 / E / D / Q / M)")
    undefined = spec.references(spec.text) - set(spec.defined)
    for ident in sorted(undefined):
        errors.append(f"spec.md: {ident} is referenced but never defined")
    if not spec.live("R"):
        errors.append("spec.md: no requirements (§5 needs at least one **" + p + "-R01**)")
    if spec.status == "✅" and spec.open_q:
        errors.append(f"spec.md: approved but questions still open: {', '.join(spec.open_q)}")
    elif spec.open_q:
        warns.append(f"open questions: {', '.join(spec.open_q)}")
    if plan is not None:
        since, drift = spec_drift(docs, feature, plan)
        if since is None:
            warns.append("plan.md: header has no **Spec:** … commit <sha> — drift can't be checked")
        elif drift:
            warns.append(f"spec.md changed since the plan was approved ({since}): " + "; ".join(drift))
        if spec.status != "✅":
            errors.append("plan.md exists but the spec is not ✅ approved")
    if tasks is not None:
        for tid, n in tasks.duplicates:
            errors.append(f"tasks.md:{n}: {tid} used twice")
        for tid, t in sorted(tasks.tasks.items()):
            for ident in sorted(t["ids"]):
                if ident not in spec.defined:
                    errors.append(f"tasks.md:{t['line']}: {tid} covers unknown {ident}")
                elif ident in spec.withdrawn:
                    errors.append(f"tasks.md:{t['line']}: {tid} covers withdrawn {ident}")
            for dep in t["after"]:
                if dep not in tasks.tasks:
                    errors.append(f"tasks.md:{t['line']}: {tid} is after unknown {dep}")
            if not t["ids"] and not t["setup"]:
                errors.append(f"tasks.md:{t['line']}: {tid} covers no requirement (write `covers: setup` if on purpose)")
        for ident in spec.live("RE"):
            if not tasks.covering(ident):
                errors.append(f"tasks.md: {ident} has no task")
    for e in errors:
        print("ERROR", e)
    for w in warns:
        print("WARN ", w)
    n_tasks = len(tasks.tasks) if tasks else 0
    print(f"{feature} ({p}, {spec.status or '?'}): {len(spec.live('R'))} requirements, "
          f"{len(spec.live('E'))} edge cases, {len(spec.open_q)} open questions, {n_tasks} tasks — "
          f"{len(errors)} errors, {len(warns)} warnings")
    return 1 if errors else 0


# ---------------------------------------------------------------- trace

def scan_tests(repo, prefix):
    """ID -> [path:line] for test files in a repo that name the ID."""
    found = {}
    # `_` is a word character, so \b would miss pytest names like test_brn_r01_creates
    id_re = re.compile(r"(?<![A-Za-z0-9])(" + re.escape(prefix) + r")[-_]([RE])(\d{2,3})(?!\d)", re.IGNORECASE)
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for name in files:
            if not name.endswith(TEXT_EXT):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, repo)
            if not TEST_PATH_RE.search(rel):
                continue
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    for n, line in enumerate(f, 1):
                        for m in id_re.finditer(line):
                            ident = f"{m.group(1).upper()}-{m.group(2).upper()}{m.group(3)}"
                            loc = f"{os.path.basename(repo)}/{rel}:{n}"
                            if loc not in found.setdefault(ident, []):
                                found[ident].append(loc)
            except OSError:
                pass
    return found


def scan_qa(repo, feature, prefix):
    """ID -> list of (result, scenario, report) from the latest QA report in the repo."""
    qdir = os.path.join(repo, "qa-reports")
    if not os.path.isdir(qdir):
        return {}, None
    # qa-method names reports <date>-<feature>[-N].md; plain string sorting would put "-2.md" before ".md"
    name_re = re.compile(r"^(\d{4}-\d{2}-\d{2})-" + re.escape(feature) + r"(?:-(\d+))?\.md$")
    reports = []
    for f in os.listdir(qdir):
        m = name_re.match(f)
        if m:
            reports.append((m.group(1), int(m.group(2) or 1), f))
    if not reports:
        return {}, None
    latest = max(reports)[2]
    text = read(os.path.join(qdir, latest)) or ""
    row_re = re.compile(r"^\|\s*(" + re.escape(prefix) + r"-[RE]\d{2,3})-([CVM]\d+)\s*\|(.*)\|\s*$")
    out = {}
    for line in text.splitlines():
        m = row_re.match(line)
        if not m:
            continue
        cells = m.group(3)
        result = "❌" if "❌" in cells else "⚠️" if "⚠️" in cells else "⏭️" if "⏭️" in cells \
            else "✅" if "✅" in cells else "?"
        out.setdefault(m.group(1), []).append((result, f"{m.group(1)}-{m.group(2)}", latest))
    return out, f"{os.path.basename(repo)}/qa-reports/{latest}"


def cmd_trace(docs, feature, repos, write=True):
    fdir, spec, plan, tasks = load(docs, feature)
    p = spec.prefix
    plan_refs = spec.references(plan or "")
    tests, qa, qa_reports = {}, {}, []
    for repo in repos:
        if not os.path.isdir(repo):
            die(f"Not a folder: {repo}")
        for k, v in scan_tests(repo, p).items():
            tests.setdefault(k, []).extend(v)
        q, rep = scan_qa(repo, feature, p)
        for k, v in q.items():
            qa.setdefault(k, []).extend(v)
        if rep:
            qa_reports.append(rep)

    rows, counts = [], {}
    for ident in spec.ids("RE"):
        if ident in spec.withdrawn:
            continue
        tids = tasks.covering(ident) if tasks else []
        done = [t for t in tids if tasks.tasks[t]["done"] and not tasks.tasks[t]["stale"]]
        stale = [t for t in tids if tasks.tasks[t]["stale"]]
        results = [r for r, _, _ in qa.get(ident, [])]
        if tasks is not None and not tids:
            status = "⛔ no task"
        elif "❌" in results:
            status = "❌ QA failing"
        elif stale:
            status = "⟳ stale"
        elif tids and len(done) < len(tids):
            status = "🔨 in progress"
        elif not tests.get(ident) and "✅" not in results:
            status = "⚠️ untested"
        else:
            status = "✅ covered"
        counts[status] = counts.get(status, 0) + 1
        task_cell = " ".join(f"{t}{'✓' if t in done else '⟳' if t in stale else '·'}" for t in tids) or "—"
        test_cell = "<br>".join(f"`{l}`" for l in tests.get(ident, [])[:4]) or "—"
        if len(tests.get(ident, [])) > 4:
            test_cell += f"<br>+{len(tests[ident]) - 4} more"
        qa_cell = " ".join(f"{s.split('-')[-1]}{r}" for r, s, _ in qa.get(ident, [])) or "—"
        rows.append(f"| {ident} | {'✓' if ident in plan_refs else '—'} | {task_cell} | {test_cell} | {qa_cell} | {status} |")

    drift = []
    since, changed = spec_drift(docs, feature, plan)
    if changed:
        drift.append(f"spec.md changed after the plan was approved (`{since}`): " + "; ".join(changed))
    for source, ids in (("tests", tests), ("QA", qa)):
        for ident in sorted(ids):
            if ident not in spec.defined:
                drift.append(f"{source} name {ident}, which the spec doesn't define: " +
                             ", ".join(f"`{l}`" if isinstance(l, str) else l[1] for l in ids[ident][:3]))
            elif ident in spec.withdrawn:
                drift.append(f"{source} still name withdrawn {ident}")
    if tasks:
        for tid, t in sorted(tasks.tasks.items()):
            for ident in t["ids"]:
                if ident in spec.withdrawn:
                    drift.append(f"{tid} covers withdrawn {ident}")

    total = sum(counts.values())
    summary = " · ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "nothing to trace"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    repo_names = ", ".join(os.path.basename(os.path.abspath(r)) for r in repos) or "none"
    out = [
        f"# Trace: {feature}",
        "",
        f"> Generated by `sddtool.py trace` on {now} — **do not edit by hand**; run `/sdd:trace {feature}`.",
        "",
        f"**Spec:** {p} {spec.status or '?'} · **Repos scanned:** {repo_names} · "
        f"**QA reports:** {', '.join(qa_reports) or 'none'}",
        "",
        f"**{total} requirements and edge cases:** {summary}",
        "",
        "| ID | Plan | Tasks | Tests | QA | Status |",
        "|---|---|---|---|---|---|",
        *rows,
        "",
        "## Drift",
        "",
        *([f"- {d}" for d in drift] or ["None."]),
        "",
    ]
    if write:
        with open(os.path.join(fdir, "trace.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(out))
    print(f"{feature}: {summary}; drift {len(drift)}" + ("" if write else " (not written)"))
    for d in drift:
        print("DRIFT", d)
    for r in rows:
        if "✅" not in r.rsplit("|", 2)[-2]:
            print("OPEN ", r.split("|")[1].strip(), r.rsplit("|", 2)[-2].strip())
    clean = not drift and counts.get("✅ covered", 0) == total
    return 0 if clean else 1


# ---------------------------------------------------------------- status

def cmd_status(docs):
    sdir = os.path.join(docs, "specs")
    if not os.path.isdir(sdir):
        die(f"No specs/ folder in {docs}")
    print("| Feature | Prefix | Spec | Open Q | Plan | Tasks | Trace |")
    print("|---|---|---|---|---|---|---|")
    for feature in sorted(os.listdir(sdir)):
        fdir = os.path.join(sdir, feature)
        if feature.startswith(("_", ".")) or not os.path.isfile(os.path.join(fdir, "spec.md")):
            continue
        spec = Spec(read(os.path.join(fdir, "spec.md")))
        plan = read(os.path.join(fdir, "plan.md"))
        tasks_text = read(os.path.join(fdir, "tasks.md"))
        tcell = "—"
        if tasks_text is not None and spec.prefix:
            t = Tasks(tasks_text, spec.prefix).tasks
            tcell = f"{sum(1 for v in t.values() if v['done'])}/{len(t)}"
            stale = sum(1 for v in t.values() if v["stale"])
            if stale:
                tcell += f" ({stale}⟳)"
        trace = read(os.path.join(fdir, "trace.md"))
        trcell = "—"
        if trace:
            m = re.search(r"^\*\*(\d+) requirements and edge cases:\*\*\s*(.*)$", trace, re.M)
            trcell = m.group(2) if m else "?"
        _, drift = spec_drift(docs, feature, plan)
        pcell = "—" if plan is None else ("⚠️ spec changed" if drift else "✓")
        print(f"| {feature} | {spec.prefix or '?'} | {spec.status or '?'} | {len(spec.open_q)} | "
              f"{pcell} | {tcell} | {trcell} |")
    return 0


def main(argv):
    if len(argv) < 2:
        die(__doc__)
    cmd, args = argv[1], argv[2:]
    write = "--no-write" not in args
    args = [a for a in args if a != "--no-write"]
    if cmd == "check" and len(args) == 2:
        return cmd_check(os.path.abspath(args[0]), args[1])
    if cmd == "trace" and len(args) >= 2:
        return cmd_trace(os.path.abspath(args[0]), args[1], [os.path.abspath(r) for r in args[2:]], write)
    if cmd == "status" and len(args) == 1:
        return cmd_status(os.path.abspath(args[0]))
    die(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
