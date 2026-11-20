#!/usr/bin/env python3
"""Build the reading library.

Each book lives in its own folder next to this one (e.g. ../wuthering-heights/) with:
  book.json        title, author, fonts, cover colours, light/dark theme tokens
  emblem.svg       the book's emblem (drawn with currentColor)
  text/chNN.txt    chapter text, paragraphs separated by blank lines
  notes/chNN.json  {"orient": ..., "notes": [...]}  (see that book's ANNOTATION_GUIDE.md)

Outputs in ../dist/:
  index.html             the published page (no doc skeleton; the host adds it)
  data/<book-id>.json    one book's chapters and notes, fetched by the page
  offline.html           a standalone copy with all data inline, to open from disk
"""
import json
import pathlib
import re

SITE = pathlib.Path(__file__).parent
ROOT = SITE.parent
DIST = ROOT / "dist"
BOOKS = ["wuthering-heights"]  # shelf order

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV",
         "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI",
         "XXVII", "XXVIII", "XXIX", "XXX", "XXXI", "XXXII", "XXXIII", "XXXIV", "XXXV", "XXXVI",
         "XXXVII", "XXXVIII", "XXXIX", "XL"]


def load_book(book_id):
    folder = ROOT / book_id
    meta = json.loads((folder / "book.json").read_text(encoding="utf-8"))
    emblem = (folder / "emblem.svg").read_text(encoding="utf-8").strip()
    emblem = re.sub(r"<!--.*?-->", "", emblem, flags=re.S)
    emblem = re.sub(r">\s+<", "><", emblem)
    chapters, n_notes, n_pass = [], 0, 0
    vb = meta.get("volumeBreak")
    for n in range(1, meta["chapters"] + 1):
        text = folder / "text" / f"ch{n:02d}.txt"
        notes = folder / "notes" / f"ch{n:02d}.json"
        ch = {"n": n, "roman": ROMAN[n - 1],
              "volnote": f"Volume II, Chapter {ROMAN[n - vb]} in two-volume editions" if vb and n >= vb else ""}
        if text.exists() and notes.exists():
            paras = [p.strip() for p in text.read_text(encoding="utf-8").split("\n\n") if p.strip()]
            data = json.loads(notes.read_text(encoding="utf-8"))
            ch.update(paras=paras, orient=data.get("orient", ""), notes=data["notes"])
            n_notes += len(data["notes"])
            n_pass += sum(1 for x in data["notes"] if "s" in x)
        chapters.append(ch)
    shelf = {k: meta[k] for k in ("id", "title", "author", "year", "blurb", "fonts", "cover")}
    shelf.update(emblem=emblem, source=meta.get("source", ""),
                 chapters=[{"n": c["n"], "roman": c["roman"], "ready": "paras" in c} for c in chapters],
                 stats={"chapters": sum(1 for c in chapters if "paras" in c), "notes": n_notes, "passages": n_pass})
    return meta, shelf, {"id": book_id, "chapters": chapters}


def theme_css(meta):
    sel = f':root[data-book="{meta["id"]}"]'

    def block(tokens, extra=""):
        return "; ".join(f"--{k}: {v}" for k, v in tokens.items()) + extra

    f = meta["fonts"]
    fonts = f'--f-display: {f["display"]}; --f-body: {f["body"]}; --display-style: {f.get("displayStyle", "normal")}; --display-weight: {f.get("displayWeight", "500")}'
    light, dark = meta["theme"]["light"], meta["theme"]["dark"]
    return (f"{sel} {{ {block(light)}; {fonts} }}\n"
            f'@media (prefers-color-scheme: dark) {{ {sel}:not([data-theme="light"]) {{ {block(dark)}; color-scheme: dark }} }}\n'
            f'{sel}[data-theme="dark"] {{ {block(dark)}; color-scheme: dark }}\n')


def js_safe(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def main():
    shelf, themes, data = [], [], {}
    for book_id in BOOKS:
        meta, s, d = load_book(book_id)
        shelf.append(s)
        themes.append(theme_css(meta))
        data[book_id] = d
    app = (SITE / "app.html").read_text(encoding="utf-8")
    app = app.replace("/*__THEMES__*/", "".join(themes))
    page = app.replace("/*__SHELF__*/[]", js_safe(shelf))

    (DIST / "data").mkdir(parents=True, exist_ok=True)
    (DIST / "index.html").write_text(page.replace("/*__INLINE__*/null", "null"), encoding="utf-8")
    for book_id, d in data.items():
        (DIST / "data" / f"{book_id}.json").write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    skeleton = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                '<style>body{margin:0}[hidden]{display:none!important}</style>\n</head>\n<body>\n')
    offline = page.replace("/*__INLINE__*/null", js_safe(data))
    (DIST / "offline.html").write_text(skeleton + offline + "\n</body>\n</html>\n", encoding="utf-8")
    for s in shelf:
        print(f"{s['title']}: {s['stats']['chapters']} chapters, {s['stats']['notes']} notes, {s['stats']['passages']} dialect passages")
    print(f"Wrote {DIST}/index.html, offline.html and data/")


if __name__ == "__main__":
    main()
