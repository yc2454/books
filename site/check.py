#!/usr/bin/env python3
"""Check notes/chNN.json against text/chNN.txt using the same matching rules as the page.

Usage: python3 site/check.py <book-folder> 6 7 8   (or just the folder, for every chapter with notes)
e.g.   python3 site/check.py as-i-lay-dying 1 2 3

Reports notes that will never appear on the page:
  NOT FOUND  - the text (or passage start/end) is not in the chapter as written
  HIDDEN     - found, but always swallowed by a longer overlapping note
plus basic format problems. A clean chapter prints "OK".
"""
import json, pathlib, re, sys

BOOKS = pathlib.Path(__file__).parent.parent
ROOT = None  # set from the first argument
CATS = set()


def forms(t):
    out = {t}
    f = t[0]
    if f.lower() != f.upper():
        out.add((f.upper() if f == f.lower() else f.lower()) + t[1:])
    return out


def render(paras, notes):
    used, shown = set(), set()
    for raw in paras:
        if re.fullmatch(r"(\*\s*)+", raw):
            continue
        plain = raw.replace("_", "")
        passes = []
        for i, n in enumerate(notes):
            if "s" not in n or i in used:
                continue
            a = plain.find(n["s"])
            if a == -1:
                continue
            b = plain.find(n["e"], a + len(n["s"]) - min(len(n["s"]), len(n["e"])))
            if b == -1:
                continue
            passes.append((a, b + len(n["e"]), i))
        passes.sort()
        chosen_p = []
        for P in passes:
            if chosen_p and P[0] < chosen_p[-1][1]:
                continue
            chosen_p.append(P); used.add(P[2]); shown.add(P[2])

        def crosses(s, e):
            return any(s < P[1] and e > P[0] and not (s >= P[0] and e <= P[1]) for P in chosen_p)

        found = []
        for i, n in enumerate(notes):
            if "s" in n or (n.get("first") and i in used):
                continue
            for f in forms(n["t"]):
                at = plain.find(f)
                while at != -1:
                    end = at + len(f)
                    ok_s = not f[0].isalpha() or at == 0 or not plain[at - 1].isalpha()
                    ok_e = not f[-1].isalpha() or end >= len(plain) or not plain[end].isalpha()
                    if ok_s and ok_e and not crosses(at, end):
                        found.append((at, end, i))
                    at = plain.find(f, at + 1)
        found.sort(key=lambda m: (m[0], -(m[1] - m[0])))
        cur = 0
        for s, e, i in found:
            if s < cur or (notes[i].get("first") and i in used):
                continue
            cur = e; used.add(i); shown.add(i)
    return shown


def check(n):
    tp, np_ = ROOT / "text" / f"ch{n:02d}.txt", ROOT / "notes" / f"ch{n:02d}.json"
    if not np_.exists():
        print(f"ch{n}: no notes file"); return False
    paras = [p.strip() for p in tp.read_text(encoding="utf-8").split("\n\n") if p.strip()]
    try:
        data = json.loads(np_.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ch{n}: INVALID JSON: {e}"); return False
    notes = data.get("notes", [])
    problems = []
    if not data.get("orient"):
        problems.append("missing 'orient'")
    seen = set()
    for i, x in enumerate(notes):
        label = x.get("t") or x.get("s") or f"#{i}"
        if x.get("c") not in CATS:
            problems.append(f"bad category {x.get('c')!r}: {label!r}")
        if "s" in x:
            if not (x.get("e") and x.get("tr")):
                problems.append(f"passage needs s, e and tr: {label!r}")
        elif not (x.get("t") and x.get("g")):
            problems.append(f"note needs t and g: {label!r}")
        key = x.get("t") or x.get("s")
        if key in seen:
            problems.append(f"duplicate: {key!r}")
        seen.add(key)
    plain = "\n".join(paras).replace("_", "")
    shown = render(paras, notes)
    for i, x in enumerate(notes):
        if i in shown:
            continue
        label = x.get("t") or x.get("s")
        missing = [k for k in ("t", "s", "e") if k in x and x[k] not in plain]
        problems.append(f"{'NOT FOUND' if missing else 'HIDDEN'}: {label!r}")
    npass = sum(1 for x in notes if "s" in x)
    if problems:
        print(f"ch{n}: {len(notes)} notes ({npass} passages), {len(problems)} problem(s):")
        for p in problems:
            print("   -", p)
        return False
    print(f"ch{n}: OK, {len(notes)} notes ({npass} passages)")
    return True


if __name__ == "__main__":
    ROOT = BOOKS / sys.argv[1]
    CATS.update(json.loads((ROOT / "book.json").read_text(encoding="utf-8"))["categories"])
    nums = [int(a) for a in sys.argv[2:]] or [i for i in range(1, 35) if (ROOT / "notes" / f"ch{i:02d}.json").exists()]
    ok = all([check(i) for i in nums])
    sys.exit(0 if ok else 1)
