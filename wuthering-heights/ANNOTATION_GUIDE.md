# Annotation guide: Wuthering Heights companion

This project is an interactive reading companion for *Wuthering Heights*. The reader has a printed copy and keeps this page open beside it. Tapping an underlined word or phrase shows a note. The reader is a smart modern adult who speaks American English. They are not a specialist, and they find 19th-century British English, Yorkshire dialect and farm life hard. **Your job is to write the notes for some chapters.**

Read these first to absorb the style:
- `notes/ch04.json` and `notes/ch05.json`: the house style for ordinary notes
- `notes/ch02.json` and `notes/ch03.json`: dialect passages (entries with `s`/`e`/`tr`)

## Files

- `text/chNN.txt`: the chapter text, one paragraph per block, separated by blank lines. `_underscores_` mark italics. Never edit these.
- `notes/chNN.json`: you create one for each of your chapters.
- `python3 check.py N`: validates chapter N with the page's exact matching rules. Run it until it prints `OK`.

Only create or edit the `notes/chNN.json` files for **your** chapters. Don't touch other files. Don't run `build.py`: other people are working at the same time.

## JSON format

```json
{
  "orient": "Narrator: ... (2–3 sentences, see below)",
  "notes": [
    {"t": "pious ejaculation", "c": "shift", "g": "A short, sudden religious exclamation.", "m": "'Ejaculation' meant any short burst of speech ...", "n": "Optional longer note."},
    {"t": "Juno", "c": "name", "first": true, "g": "The female pointer who attacked Lockwood in Chapter I."},
    {"s": "What are ye for?", "e": "if ye went to spake to him.", "c": "dialect", "who": "Joseph", "tr": "What do you want? The master's down in the fold ..."}
  ]
}
```

Word or phrase note:
- `t`: the exact text as printed in the chapter, copied character for character, including curly quotes and apostrophes (’ “ ”) and hyphens. Leave out the `_` italic markers.
- `c`: category (see below).
- `g`: gloss. A short plain-English meaning, usually under 12 words, ending with a full stop.
- `m`: only for changed meanings: what the word does *not* mean here (the modern sense a reader would wrongly assume). Shown under the heading "Watch out:".
- `n`: optional, 1–3 short sentences of context: why it matters, a fun fact, a cross-reference ("see Chapter III").
- `first: true`: underline only the first occurrence in the chapter. Use this for names; otherwise every occurrence in the chapter is underlined.

Dialect passage (a whole speech in thick dialect):
- `s` and `e`: exact snippets at the start and end of the speech, in the **same paragraph**. `e` must come after `s`. Use about 3–8 words each, and keep them distinctive.
- `tr`: the whole speech in natural modern English.
- `who`: the speaker. `c` is always `"dialect"`. `n` is optional.
- Word notes inside a passage still work. Add notes for the key dialect words inside it too ("laiking", "lugs").

## Categories

| c | label | use for |
|---|---|---|
| `shift` | Changed meaning | Words that look familiar but meant something different then: "homely", "dinner", "intercourse", "presently", "directly", "rude", "nice", "gay", "condescend", "sensible", "interesting", "let" (rent). These are the most valuable notes because readers don't know they misread them. Always give `m`. |
| `old` | Old or literary word | Archaic, formal, rare or Latinate words: "ere", "hitherto", "physiognomy", "laconic"; Lockwood's pompous vocabulary; idioms like "box his ears". |
| `rural` | Farm and country life | Farm work, animals, buildings, tools, food, moorland landscape: "fold", "flags", "peat", "beck", "oatcakes", "under-drawn". |
| `dialect` | Yorkshire dialect | Dialect words and spellings: "nobbut", "laik", "lugs", "mun", "flaysome", "barn" (= bairn, child). |
| `ref` | Reference and context | Bible and Shakespeare allusions, religion (Joseph's Calvinism), law and inheritance, money, social class, customs, medicine, period facts, foreshadowing. |
| `name` | People and places | Characters and places when they first appear or when a name is ambiguous. Use `first: true`. |

## How much to annotate

Be generous. Earlier chapters have about 40–55 notes per 1,000 words. Annotate anything a modern American reader might not know, might misread, or would enjoy knowing:
- Every shifted meaning.
- Archaic and formal words, even fairly common ones such as "countenance", "ere" and "vexed".
- British words an American may not know ("frock", "lumber", "fortnight").
- Farm, food, clothing, household and money details.
- Allusions, especially to the Bible.
- Every speech in thick dialect gets a passage with `tr`: Joseph, and also Hareton, Zillah, Hindley, the old master and others when they speak dialect. Short dialect lines ("Hey, holld him!") can be plain word notes instead.

Notes can repeat words that were glossed in earlier chapters. Each chapter stands alone.

## Spoilers: the most important rule

The reader is reading chapter by chapter, for the first time. A note in chapter N may use **only what the book has revealed by that point in chapter N**. You know the whole novel, so be very careful:
- Don't name anyone before the text names them. Don't say who a character "really" is, who they will marry, whether they die, or how a plot thread ends.
- Don't hint at what is coming ("this will have terrible consequences"). A neutral "keep this in mind" is fine, and so is pointing back to earlier chapters.
- Name notes describe a person only as far as the story so far has shown them.
- Do help with confusing names, within those limits. There are two Catherines (old Cathy and young Cathy), and "Linton" can mean Edgar, the Linton family, Isabella's married name or (later) Heathcliff's son. Say which one is meant here if the text makes it clear.

## Orientation line (`orient`)

Two or three sentences: who is narrating (Nelly to Lockwood, Lockwood's diary, Isabella's letter, and so on), roughly when (for example "Scholars date this to the winter of 1777–78", but give a year only when you are confident from the standard chronology; otherwise say "a few months later"), and any frame shift ("Lockwood interrupts Nelly's story here"). Make it spoiler-free: describe the situation at the start of the chapter, not what happens.

## Style

- Plain, friendly, direct sentences. No jargon. Avoid dashes as asides.
- In `g`, `m` and `n`, use straight quotes and apostrophes ('like this'). Only `t`, `s` and `e` must copy the text's curly characters exactly.
- Gloss the meaning *in this context*, not a dictionary list.
- Facts must be accurate. If unsure about a dialect word, say "probably" or leave it out.

## Matching rules (what `check.py` enforces)

- `t` is matched as whole words: a match can't start or end in the middle of a word. The first letter's case is flexible ("Nay" matches "nay"). Everything else must match exactly.
- A note on a common word underlines **every** occurrence in the chapter. If the word is used in different senses, use a longer phrase as `t` to pin down the one you mean.
- When two notes overlap, the one that starts earlier wins, and if they start together, the longer one wins. The other is HIDDEN there. Don't put a note entirely inside another word note. Inside a dialect passage, word notes are fine.
- `check.py` must print `OK` for each of your chapters before you finish.
