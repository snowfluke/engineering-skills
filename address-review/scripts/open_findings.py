#!/usr/bin/env python3
"""List the OPEN findings of a lead-review round, with what each one asks for.

  open_findings.py ROUND_FILE
  open_findings.py --self-test

ROUND_FILE holds the body of the latest review that starts with "## Round".
The output lists BLOCKERs first, then QUESTIONs, then NITs, each with its
Where, Fix, and Done when (or Question and Bug if). Standard library only.
"""
import re
import sys

ROW_RE = re.compile(r"^\| (F\d+) \| (.+) \| (BLOCKER|NIT|QUESTION) \| (OPEN|RESOLVED|DECLINED|ANSWERED) \|$")
# The middle dot is the separator of rounds posted before the ASCII switch.
HEAD_RE = re.compile(r"^### (F\d+) (?:\||\u00b7) (.+) (?:\||\u00b7) (BLOCKER|NIT|QUESTION)$")
FIELD_RE = re.compile(r"^\*\*(Where|Problem|Fix|Done when|Question|Bug if):\*\* (.+)$")
ORDER = {"BLOCKER": 0, "QUESTION": 1, "NIT": 2}


def open_findings(body):
    rows = [ROW_RE.match(l) for l in body.splitlines()]
    rows = {m[1]: (m[2], m[3]) for m in rows if m and m[4] == "OPEN"}
    fields, cur = {}, None
    for line in body.splitlines():
        h = HEAD_RE.match(line)
        if h:
            cur = h[1]
            fields[cur] = {}
            continue
        f = FIELD_RE.match(line)
        if cur and f:
            fields[cur][f[1]] = f[2]
    out = []
    for fid, (title, sev) in rows.items():
        out.append({"id": fid, "title": title, "severity": sev, **fields.get(fid, {})})
    return sorted(out, key=lambda x: (ORDER[x["severity"]], int(x["id"][1:])))


def render(findings):
    if not findings:
        return "No OPEN findings.\n"
    lines = []
    for f in findings:
        lines.append(f"{f['id']} {f['severity']}: {f['title']}")
        for key in ("Where", "Problem", "Fix", "Done when", "Question", "Bug if"):
            if key in f:
                lines.append(f"  {key}: {f[key]}")
    return "\n".join(lines) + "\n"


def self_test():
    body = """## Round 2 | Request Changes

**Gate:** passes.
**CI:** Passes.

| ID | Finding | Severity | Status |
|----|---------|----------|--------|
| F1 | Guard rejects owners | BLOCKER | RESOLVED |
| F2 | Dead check | NIT | OPEN |
| F3 | Retry source | QUESTION | OPEN |
| F4 | Missing test | BLOCKER | OPEN |

---

### F2 | Dead check | NIT

**Where:** `b.ts:9`
**Problem:** The null check never fires.
**Fix:** Delete the check.
**Done when:** The line is gone and `tsc` passes.

---

### F3 | Retry source | QUESTION

**Where:** `c.ts:4`
**Question:** Does the vendor cap retries at 3?
**Bug if:** The vendor allows fewer than 5 retries.

---

### F4 | Missing test | BLOCKER

**Where:** `a.test.ts:10`
**Problem:** The owner branch has no test.
**Fix:** Add a test for the owner.
**Done when:** A guard that always throws fails the test.
"""
    found = open_findings(body)
    assert [f["id"] for f in found] == ["F4", "F3", "F2"], found
    assert found[0]["Done when"] == "A guard that always throws fails the test."
    assert found[1]["Bug if"].startswith("The vendor")
    assert "F1" not in render(found), "a RESOLVED finding must not be listed"
    assert render([]) == "No OPEN findings.\n"
    legacy = "\n".join(l.replace(" | ", " \u00b7 ") if l.startswith("### F") else l for l in body.split("\n"))
    assert open_findings(legacy) == found, "a round with the old middle-dot headings must parse"
    print("self-test OK")


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    if len(argv) != 1:
        sys.exit(__doc__)
    with open(argv[0], encoding="utf-8") as f:
        sys.stdout.write(render(open_findings(f.read())))


if __name__ == "__main__":
    main(sys.argv[1:])
