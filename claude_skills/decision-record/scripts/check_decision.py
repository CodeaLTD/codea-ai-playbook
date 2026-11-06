#!/usr/bin/env python3
"""Check a decision.md against the decision-record layout and language rules.

    python check_decision.py requirements/decision.md

Prints one line per problem as file:line: problem, then a summary. Writes nothing.
"possible passive" lines are hints to read by hand; they do not count as problems.
Code fences (the copied diagram, the Mermaid chart) are skipped.

Exit codes: 0 nothing to fix, 1 problems found, 2 file not found.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MAX_LINES, TARGET_LINES = 550, (400, 500)
MAX_COLS, MAX_CELL_WORDS, MAX_SENTENCE, MAX_PARA_LINES, MAX_PARA_WORDS = 5, 20, 20, 2, 40
TAGS = ("[DECIDED]", "[PROPOSED]", "[OPEN]", "[NOT SPECIFIED]", "[CONFLICT]")
PLAIN = re.compile(
    r"\b(leverag\w*|utili[sz]\w*|mitigat\w*|rationale|residual\w*|obtain\w*|subsequently|"
    r"prior to|in order to|ensur(?:e|es|ed|ing)|facilitat\w*|robust\w*|comprehensive\w*|"
    r"tenancy|traceability)\b",
    re.I,
)
LATIN = re.compile(r"(?<!\w)(e\.g\.|i\.e\.|etc\b\.?)", re.I)
PASSIVE = re.compile(
    r"\b(?:is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?(?:\w+ed|built|chosen|done|found|given|"
    r"held|kept|known|left|made|put|read|run|seen|sent|set|shown|taken|told|written)\b",
    re.I,
)
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️]")
ABBREV = re.compile(r"(?<![\w-])([A-Z][A-Z0-9&]*[A-Z]s?)(?![\w-])")
NOT_ABBREV = {"ID", "IDs", "OK", "NEW", "NOT", "AND", "OR", "EXACTLY", "VERBATIM", "EVERY"}
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'“(\[*`])")
LIST_ITEM = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+(.*)$")
SEPARATOR = re.compile(r"^\|?\s*:?-{2,}")


def visible(text: str) -> str:
    """Text a reader sees: inline code becomes one word, links keep their text."""
    text = re.sub(r"`[^`]*`", "code", text)  # lower case, so it never reads as an abbreviation
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return text.replace("*", "")


def words(text: str) -> int:
    return sum(1 for t in visible(text).split() if re.search(r"\w", t))


def sentences(text: str) -> list[str]:
    return [s for s in SENTENCE_END.split(visible(text).strip()) if words(s)]


def cells(row: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<!\\)\|", row.strip().strip("|"))]


def check(path: Path) -> tuple[list[str], list[str], dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    name = path.name
    problems, hints = [], []
    units = []  # (line, text) checked for sentence length

    def problem(n: int, msg: str) -> None:
        problems.append(f"{name}:{n}: {msg}")

    # Pass 1: which lines are code, and the indent unit of nested bullets.
    code, in_code = set(), False
    for n, raw in enumerate(lines, 1):
        if raw.strip().startswith(("```", "~~~")):
            in_code = not in_code
            code.add(n)
        elif in_code:
            code.add(n)
    indents = [
        len(m.group(1).expandtabs(4))
        for n, raw in enumerate(lines, 1)
        if n not in code and (m := LIST_ITEM.match(raw)) and m.group(1)
    ]
    unit = min(indents) if indents else 2

    # Glossary terms.
    glossary, in_glossary, found_glossary = set(), False, False
    for n, raw in enumerate(lines, 1):
        s = raw.strip()
        if s.startswith("#"):
            in_glossary = "glossary" in s.lower()
            found_glossary = found_glossary or in_glossary
        elif in_glossary and s.startswith("|") and not SEPARATOR.match(s):
            term = cells(s)[0]
            glossary.add(term)
            glossary.update(ABBREV.findall(term))
    if not found_glossary:
        problem(1, "no Glossary section found")

    # Pass 2: every line outside code.
    para, header_cols, last_kind = [], None, None
    abbrevs: dict[str, int] = {}

    def flush() -> None:
        if para:
            text = " ".join(t for _, t in para)
            if len(para) > MAX_PARA_LINES or words(text) > MAX_PARA_WORDS:
                problem(para[0][0], f"paragraph over {MAX_PARA_LINES} lines ({len(para)} lines, {words(text)} words)")
            units.append((para[0][0], text))
            para.clear()

    for n, raw in enumerate(lines, 1):
        s = raw.strip()
        if n in code or not s:
            flush()
            header_cols, last_kind = None, None
            continue
        shown = visible(s)
        for tag in TAGS:
            shown = shown.replace(tag, " ")
        for m in PLAIN.finditer(shown):
            problem(n, f'plain-English word: "{m.group(0)}"')
        for m in LATIN.finditer(shown):
            problem(n, f'"{m.group(0)}": write "for example", "that is", or list the items')
        if m := EMOJI.search(s):
            problem(n, f'emoji or symbol "{m.group(0)}": use the label words (Full / Partial / Gap and so on)')
        for m in PASSIVE.finditer(shown):
            hints.append(f'{name}:{n}: possible passive (check by hand): "{m.group(0)}"')
        for a in ABBREV.findall(shown):
            abbrevs.setdefault(a, n)

        if s.startswith("|"):
            flush()
            row = cells(s)
            if SEPARATOR.match(s):
                continue
            if header_cols is None:
                header_cols = len(row)
                if header_cols > MAX_COLS:
                    problem(n, f"table has {header_cols} columns (max {MAX_COLS})")
            for c in row:
                if words(c) > MAX_CELL_WORDS:
                    problem(n, f"table cell over {MAX_CELL_WORDS} words ({words(c)}): \"{c[:50]}...\"")
                if len(sentences(c)) > 1:
                    problem(n, f'table cell has {len(sentences(c))} sentences: "{c[:50]}..."')
                if "<br" in c or "•" in c:
                    problem(n, "bullets or line breaks inside a table cell")
                units.append((n, c))
            first = row[0]
            if re.fullmatch(r"NFR\d+", first) and not any(t in s for t in TAGS):
                problem(n, f"{first} has no status tag")
            if re.fullmatch(r"A\d+", first) and not re.fullmatch(r"(Q[\w-]*\d[\s,]*)+|None\.?", row[-1], re.I):
                problem(n, f'{first}: last column must be a Q number or "None"')
            last_kind = "table"
            continue
        header_cols = None
        if s.startswith("#"):
            flush()
            if re.match(r"^###\s+3\.\d+", s) and not any(t in s for t in TAGS):
                problem(n, "decision heading has no status tag")
            last_kind = "heading"
            continue
        if m := LIST_ITEM.match(raw):
            flush()
            level = len(m.group(1).expandtabs(4)) // unit + 1
            if level > 2:
                problem(n, f"bullet nested {level} levels deep (max 2)")
            units.append((n, m.group(2)))
            last_kind = "list"
            continue
        if last_kind == "list" and raw[:1].isspace():
            units.append((n, s))  # continuation of a list item
            continue
        para.append((n, s.lstrip("> ")))
        last_kind = "para"
    flush()

    for a, n in sorted(abbrevs.items(), key=lambda x: x[1]):
        if a in NOT_ABBREV or a in glossary or (a.endswith("s") and a[:-1] in glossary):
            continue
        problem(n, f"abbreviation {a} is not in the Glossary")

    stats = {"lines": len(lines), "sentences": 0, "total": 0, "longest": (0, 0)}
    for n, text in units:
        for sent in sentences(text):
            w = words(sent)
            stats["sentences"] += 1
            stats["total"] += w
            stats["longest"] = max(stats["longest"], (w, n))
            if w > MAX_SENTENCE:
                problem(n, f'sentence over {MAX_SENTENCE} words ({w}): "{sent[:60]}..."')

    if len(lines) > MAX_LINES:
        problem(len(lines), f"{len(lines)} lines (hard maximum {MAX_LINES})")
    return problems, hints, stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("file", nargs="?", default="requirements/decision.md")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    path = Path(a.file)
    if not path.is_file():
        print(f"No {path}", file=sys.stderr)
        return 2
    problems, hints, st = check(path)
    for line in sorted(problems, key=lambda p: int(p.split(":")[1])) + hints:
        print(line)
    lo, hi = TARGET_LINES
    target = "" if lo <= st["lines"] <= hi else f", outside the target {lo}-{hi}"
    avg = st["total"] / st["sentences"] if st["sentences"] else 0
    w, n = st["longest"]
    print(
        f"Summary: {st['lines']} lines{target} · {st['sentences']} sentences, average {avg:.1f} words, "
        f"longest {w} (line {n}) · {len(problems)} problem(s) · {len(hints)} possible passive(s)"
    )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
