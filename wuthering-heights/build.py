#!/usr/bin/env python3
"""Build index.html from template.html + text/chNN.txt + notes/chNN.json.

Each text/chNN.txt holds one chapter, paragraphs separated by blank lines
(_underscores_ mark italics, as in the Project Gutenberg text).
Each notes/chNN.json holds {"orient": str, "notes": [...]}. A note:
  t      exact text as it appears in the chapter (matched as whole words)
  c      category: shift | old | rural | dialect | ref | name
  g      short gloss
  m      (optional) the modern sense to avoid, for changed meanings
  n      (optional) longer explanation
  first  (optional) true = mark only the first occurrence in the chapter
A dialect passage instead has:
  s, e   exact start and end snippets of the speech (same paragraph)
  tr     the speech in plain modern English
  who    (optional) speaker, e.g. "Joseph";  n (optional) note;  c = "dialect"
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII",
         "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII",
         "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX", "XXX", "XXXI",
         "XXXII", "XXXIII", "XXXIV"]


def vol_label(n):
    # Many editions restart numbering in Volume II (Vol. II ch. 1 = ch. 15).
    if n <= 14:
        return f"Volume I, Chapter {ROMAN[n - 1]}"
    return f"Volume II, Chapter {ROMAN[n - 15]}"


def main():
    chapters = []
    for n in range(1, 35):
        entry = {"n": n, "roman": ROMAN[n - 1], "vol": vol_label(n)}
        text = ROOT / "text" / f"ch{n:02d}.txt"
        notes = ROOT / "notes" / f"ch{n:02d}.json"
        if text.exists() and notes.exists():
            paras = [p.strip() for p in text.read_text(encoding="utf-8").split("\n\n") if p.strip()]
            data = json.loads(notes.read_text(encoding="utf-8"))
            entry.update(paras=paras, orient=data.get("orient", ""), notes=data["notes"])
            plain = "\n".join(paras).replace("_", "")
            missing = [x.get("t") or x["s"] for x in data["notes"]
                       if any(k in x and x[k] not in plain for k in ("t", "s", "e"))]
            for t in missing:
                print(f"  ch{n}: note text not found: {t!r}")
        chapters.append(entry)

    payload = json.dumps(chapters, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")
    html = (ROOT / "template.html").read_text(encoding="utf-8")
    html = html.replace("/*__DATA__*/null", payload)
    # artifact.html: bare page for publishing (the host adds the skeleton).
    # index.html: standalone copy to open directly in a browser.
    (ROOT / "artifact.html").write_text(html, encoding="utf-8")
    skeleton = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                '<style>body{margin:0}[hidden]{display:none!important}</style>\n</head>\n<body>\n')
    (ROOT / "index.html").write_text(skeleton + html + "\n</body>\n</html>\n", encoding="utf-8")
    done = [c["n"] for c in chapters if "paras" in c]
    print(f"Built index.html with annotated chapters: {done}")


if __name__ == "__main__":
    main()
