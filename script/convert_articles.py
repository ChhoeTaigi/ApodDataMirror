"""Build the ChhoeTaigi tables of the 詞彙學習 (vocabulary) of apod.tw.

Input is a tangloo/ directory written by fetch_articles.py: every daily
article of 逐工一幅天文圖 as served. Each article ends in a `詞彙學習`
heading followed by a table with the columns 漢羅, POJ, KIP, 華語, English —
the Taigi vocabulary of that day's text in Han-Lo, Pe̍h-ōe-jī, KPL, Mandarin
and English. Each table row becomes one row of `ApodSului` with the
ChhoeTaigi database's column names (`PojUnicode`, `PojInput`, `KipUnicode`,
`KipInput`, `HanLoTaibunPoj`, `HoaBun`, `EngBun`, `LaigoanMia`, `LaigoanBangchi`), so
the table loads without renaming, after an id `YYYYMMDD-NN` built from
the article's date and the row's position in its table. The article's title,
given on the page in the same languages minus Mandarin, is the article's
first row, `NN` 00.

Nothing is corrected: every cell is published as written on the site, and
what looks wrong (a POJ cell that is not Pe̍h-ōe-jī, an empty cell, a table
with other columns) is listed in the report.
"""
import argparse
import collections
import csv
import datetime
import html
import json
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

try:
    from poj_text import (POJ_SYLLABLE, READING_SPLIT, TONE_MARKS, _clusters,
                          _has_caron_on_bearer, poj_unicode_to_input)
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent))
    from poj_text import (POJ_SYLLABLE, READING_SPLIT, TONE_MARKS, _clusters,
                          _has_caron_on_bearer, poj_unicode_to_input)

try:
    from fetch_articles import ARTICLE_URL_TEMPLATE, read_site
except ImportError:
    from script.fetch_articles import ARTICLE_URL_TEMPLATE, read_site  # noqa: F401

TABLE_NAME = "ApodSului"           # 詞彙 sû-lūi: one row per vocabulary entry or title
REPORT_NAME = "ApodDataQuality"

# The row's id, then the columns of the ChhoeTaigi database, so the table
# loads without renaming. WordId: `YYYYMMDD-NN`, the article's date and
# the row's position in the site's table (header excluded, blank rows
# included — the `row N` of the report, so the row can be found on the page);
# 00 is the article's title, which precedes the table on the page.
COLUMNS = ["WordId", "PojUnicode", "PojInput", "KipUnicode", "KipInput", "HanLoTaibunPoj",
           "HoaBun", "EngBun", "LaigoanMia", "LaigoanBangchi"]
WORD_ID = "{date}-{row:02d}"
TITLE_ROW = 0
# LaigoanMia 來源名: the source, written the way apod.tw's FAQ asks to be credited.
LAIGOAN_MIA = "逐工一幅天文圖 https://apod.tw"

VOCAB_HEADING = "詞彙學習"
# The site's column headers → the database columns.
HEADER_COLUMNS = {"漢羅": "HanLoTaibunPoj", "POJ": "PojUnicode", "KIP": "KipUnicode",
                  "華語": "HoaBun", "English": "EngBun"}
EXPECTED_HEADERS = list(HEADER_COLUMNS)
# The article's title is repeated in four headings: `[漢羅] …`, `[POJ] …`,
# `[KIP] …`, `[English] …`. There is no Mandarin title.
TITLE_PREFIXES = {"漢羅": "HanLoTaibunPoj", "POJ": "PojUnicode", "KIP": "KipUnicode",
                  "English": "EngBun"}
# `[English] …`; a few headings wrote the tag as a link and show `English …`,
# a few have no space after the tag (`[KIP]Lâm-hong`), a few nothing after it.
TITLE_LINE = re.compile(r"^\[?(漢羅|POJ|KIP|English)\]?\s*(.*)$")

SPACES = re.compile(r"[\s 　]+")
# Pieces of a reading: split on spaces and hyphens (`--` too), as the shared
# Pe̍h-ōe-jī code does.
PIECE_SPLIT = READING_SPLIT
LATIN = re.compile(r"[A-Za-z]")
# KPL syllable, checked on the tone-stripped lowercase piece: the KPL
# initials, a KPL rhyme (oo, nn, ir/er for dialect vowels), a coda. Only
# used to flag KIP cells in the report, never to change them.
KPL_SYLLABLE = re.compile(
    r"^(ph|p|m|b|th|t|n|l|kh|k|ng|g|h|tsh|ts|s|j)?"
    r"(?:(?:[aeiou]|oo|ir|er|ee)+(?:nn)?(?:m|ng|n)?|m|ng)"
    r"(?:p|t|k|h)?$")
# What marks a piece as Pe̍h-ōe-jī or KPL as opposed to a name or a number:
# a tone mark, o͘, ⁿ (POJ); a tone mark, `oo`, `nn`, `ts` (KPL). Other
# diacritics (`Schrödinger`) are someone else's letters.
TONE_MARK_CLASS = "[" + "".join(TONE_MARKS) + "]"
POJ_MARKERS = re.compile(TONE_MARK_CLASS + "|\u0358|ⁿ")
KPL_MARKERS = re.compile(TONE_MARK_CLASS + "|oo|nn|ts")
HAS_TONE_MARK = re.compile(TONE_MARK_CLASS)
# Punctuation is not part of a piece, around it or inside it: `(gîn-sim)`,
# `"tiám"`, and `7293：Kńg` where the site put no space after the colon.
PIECE_PUNCTUATION = "()\"'“”‘’«»,.:;!?…/[]【】（）「」『』、，。：；！？"
PUNCTUATION_SPLIT = re.compile("[" + re.escape(PIECE_PUNCTUATION) + "]+")

# How many examples each report section lists.
REPORT_SAMPLE_SIZE = 50


# --- HTML -------------------------------------------------------------------

class ArticleParser(HTMLParser):
    """Collects, in document order, what an article page holds: its `<h1>`,
    the `post_date` paragraph, every `<h2>` and every `<table>` (header
    cells and body rows). Text is unescaped and whitespace-collapsed."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1 = None
        self.post_date = None
        self.events = []        # ("h2", text) | ("table", {"headers": [...], "rows": [[...]]})
        self._text = None       # list collecting the current text block
        self._block = None      # which element the text belongs to
        self._table = None
        self._row = None
        self._in_head = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table":
            self._table = {"headers": [], "rows": []}
            self._in_head = False
        elif tag == "thead":
            self._in_head = True
        elif tag == "tbody":
            self._in_head = False
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._text, self._block = [], tag
        elif tag in ("h1", "h2"):
            self._text, self._block = [], tag
        elif tag == "p" and "post_date" in (attrs.get("class") or "").split():
            self._text, self._block = [], "p"
        elif tag == "br" and self._text is not None:
            self._text.append(" ")

    def handle_endtag(self, tag):
        if self._text is not None and tag == self._block:
            text = SPACES.sub(" ", "".join(self._text)).strip()
            if tag == "h1":
                self.h1 = self.h1 if self.h1 is not None else text
            elif tag == "h2":
                self.events.append(("h2", text))
            elif tag == "p":
                self.post_date = text
            elif tag in ("td", "th"):
                self._row.append((tag, text))
            self._text, self._block = None, None
        elif tag == "tr" and self._row is not None and self._table is not None:
            cells = self._row
            header_like = bool(cells) and (self._in_head or all(t == "th" for t, _ in cells))
            if header_like and not self._table["headers"]:
                self._table["headers"] = [c for _, c in cells]
            else:
                # A second header-like row (a sub-heading, an entry written in
                # <th> cells) is kept as a row and listed in the report; nothing
                # is dropped silently.
                self._table["rows"].append([c for _, c in cells])
                if header_like:
                    self._table.setdefault("header_like_rows", []).append(len(self._table["rows"]))
            self._row = None
        elif tag == "thead":
            self._in_head = False
        elif tag == "table" and self._table is not None:
            self.events.append(("table", self._table))
            self._table = None

    def handle_data(self, data):
        if self._text is not None:
            self._text.append(data)


def parse_article(html_text):
    p = ArticleParser()
    p.feed(html_text)
    p.close()
    return p


# --- Rows -------------------------------------------------------------------

POST_DATE_FORMATS = ["%d. %B %Y"]


def post_date_to_url_date(text):
    """`13. June 2025` → `20250613`, the date as the article's URL writes it, or None."""
    for fmt in POST_DATE_FORMATS:
        try:
            return datetime.datetime.strptime(text, fmt).strftime("%Y%m%d")
        except ValueError:
            continue
    return None


def article_titles(parsed):
    """{column: title} from the `[漢羅] …` headings."""
    titles = {}
    for kind, text in parsed.events:
        if kind != "h2":
            continue
        m = TITLE_LINE.match(text)
        if m and m.group(1) in TITLE_PREFIXES:
            column = TITLE_PREFIXES[m.group(1)]
            titles.setdefault(column, m.group(2))
    return titles


def vocabulary_table(parsed):
    """(table, problem): the first table after the 詞彙學習 heading and
    before the next heading; problem names what is missing."""
    seen_heading = False
    for kind, payload in parsed.events:
        if kind == "h2":
            if payload == VOCAB_HEADING:
                seen_heading = True
            elif seen_heading:
                return None, "heading without table"
        elif kind == "table" and seen_heading:
            return payload, None
    return None, ("heading without table" if seen_heading else "no heading")


def strip_tones(text):
    return unicodedata.normalize("NFC", "".join(
        base + "".join(m for m in marks if m not in TONE_MARKS)
        for base, marks in _clusters(text)))


def _marked_pieces(text, markers):
    """The pieces of text — split on spaces, hyphens and punctuation — that
    carry one of markers, except a capitalised piece with no tone mark, which
    is a name (`Kennedy`, `Bennu`) rather than a syllable to check."""
    for chunk in PIECE_SPLIT.split(text):
        for piece in PUNCTUATION_SPLIT.split(chunk):
            nfd = unicodedata.normalize("NFD", piece)
            if not piece or not markers.search(nfd):
                continue
            if piece[0].isupper() and not HAS_TONE_MARK.search(nfd):
                continue
            yield piece


# The syllable regex (kept as the siblings have it) does not know the tone-9
# breve on a vowel other than in `̍ă`; `iăn-jín`, `khă-tián` are Pe̍h-ōe-jī.
TONE_9 = re.compile("[" + "".join(m for m, tone in TONE_MARKS.items() if tone == "9") + "]")


def _is_poj_syllable(piece):
    """The regex is written with precomposed letters, so the piece is matched
    in NFC; the cell itself is published as written."""
    if POJ_SYLLABLE.match(unicodedata.normalize("NFC", piece)):
        return True
    nfd = unicodedata.normalize("NFD", piece)
    return bool(TONE_9.search(nfd)) and bool(
        POJ_SYLLABLE.match(unicodedata.normalize("NFC", TONE_9.sub("", nfd))))


def pieces_not_poj(text):
    """The pieces of a POJ cell that carry a Pe̍h-ōe-jī marker (tone, o͘, ⁿ)
    yet are not one Pe̍h-ōe-jī syllable."""
    return [p for p in _marked_pieces(text, POJ_MARKERS) if not _is_poj_syllable(p)]


def pieces_not_kpl(text):
    """The pieces of a KIP cell that carry a KPL marker (tone, oo, nn, ts)
    yet are not one KPL syllable."""
    return [p for p in _marked_pieces(text, KPL_MARKERS)
            if not KPL_SYLLABLE.match(strip_tones(p).lower())]


def to_input(text, report, where):
    converted, multi = poj_unicode_to_input(text)
    if multi:
        report["rows"]["multi_tone"].append({"where": where, "text": text, "words": multi})
        report["counts"]["rows_multi_tone"] += 1
    return converted


def new_row(date, number, url):
    """An empty row of article `date` at position `number` (TITLE_ROW for
    the title), with its id and source columns set."""
    row = {col: "" for col in COLUMNS}
    row["WordId"] = WORD_ID.format(date=date, row=number)
    row["LaigoanMia"] = LAIGOAN_MIA
    row["LaigoanBangchi"] = url
    return row


def check_row(row, date, where, report):
    """Builds the input forms and runs the spelling checks — the same for a
    title row and a table row."""
    row["PojInput"] = to_input(row["PojUnicode"], report, where)
    row["KipInput"] = to_input(row["KipUnicode"], report, where)
    bad = pieces_not_poj(row["PojUnicode"])
    if bad:
        report["rows"]["not_poj"].append(
            {"where": where, "date": date, "text": row["PojUnicode"], "pieces": bad})
    bad = pieces_not_kpl(row["KipUnicode"])
    if bad:
        report["rows"]["not_kpl"].append(
            {"where": where, "date": date, "text": row["KipUnicode"], "pieces": bad})
    for col in ("PojUnicode", "KipUnicode"):
        if _has_caron_on_bearer(row[col]):
            report["rows"]["caron"].append({"where": f"{where} {col}", "text": row[col]})


# --- Output -----------------------------------------------------------------

def write_csv(rows, columns, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def write_json_rows(rows, path):
    """A JSON array with one record per line, for diffs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("[\n")
        for i, row in enumerate(rows):
            f.write(json.dumps(row, ensure_ascii=False))
            f.write(",\n" if i < len(rows) - 1 else "\n")
        f.write("]\n")


def write_json(payload, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")


# --- Report -----------------------------------------------------------------

def _code(text):
    return "`" + str(text).replace("`", "'").replace("|", "\\|") + "`"


def _md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c).replace("|", "\\|") for c in row) + " |" for row in rows]
    return "\n".join(out)


def _shown(items, noun):
    if len(items) > REPORT_SAMPLE_SIZE:
        return (items[:REPORT_SAMPLE_SIZE],
                f"\n\nFirst {REPORT_SAMPLE_SIZE} of {len(items):,} {noun}; "
                f"the JSON report lists them all.")
    return items, ""


def _link(date):
    return f"[{date}]({ARTICLE_URL_TEMPLATE.format(date=date)})"


def render_report_md(report):
    c = report["counts"]
    out = [f"# {REPORT_NAME}", "",
           f"Version `{report['version']}`, built from {report['source']} "
           f"(articles {report['oldest_article']} to {report['newest_article']}).", ""]

    out += ["## 1. Articles", "",
            f"- {c['articles_sitemap']:,} daily articles in `sitemap.xml`",
            f"- {c['articles_listing']:,} on the {c['listing_pages']} pages of the `/daily/` listing",
            f"- {c['articles']:,} in their union, {c['articles_fetched']:,} fetched, "
            f"{c['articles_missing']:,} answering 404",
            f"- {c['articles_with_table']:,} with a {VOCAB_HEADING} table, "
            f"{c['articles_no_heading']:,} with no {VOCAB_HEADING} heading, "
            f"{c['articles_no_table']:,} with the heading but no table",
            f"- {c['articles_empty_table']:,} with a table of no rows", ""]
    for key, title, noun in [
            ("sitemap_only", "In the sitemap but not in the listing", "articles"),
            ("listing_only", "In the listing but not in the sitemap", "articles"),
            ("missing", "Answering 404", "articles"),
            ("no_heading", f"With no {VOCAB_HEADING} heading", "articles"),
            ("no_table", f"With the heading but no table after it", "articles"),
            ("empty_table", "With a table of no rows", "articles")]:
        items = report["articles"][key]
        if not items:
            continue
        shown, note = _shown(items, noun)
        out += [f"### {title}", "", ", ".join(_link(d) for d in shown) + note, ""]

    out += ["### Titles", "",
            f"Every article's title is read from its `[漢羅]`, `[POJ]`, `[KIP]` and "
            f"`[English]` headings and is its first row in `{TABLE_NAME}` (`WordId` "
            f"ending in `-00`; `HoaBun` empty, the site has no Mandarin title). Articles "
            f"lacking one or more headings (an empty heading counts as lacking): "
            f"{c['articles_titles_incomplete']:,}. One lacking all four and the `<h1>` "
            f"would get no title row.", ""]
    if report["articles"]["titles_incomplete"]:
        shown, note = _shown(report["articles"]["titles_incomplete"], "articles")
        out += [_md_table(["Article", "Missing"],
                          [(_link(a["date"]), ", ".join(a["missing"])) for a in shown]) + note, ""]
    if report["articles"]["date_mismatch"]:
        shown, note = _shown(report["articles"]["date_mismatch"], "articles")
        out += ["### Page date differing from the URL date", "",
                _md_table(["Article", "Page says"],
                          [(_link(a["date"]), _code(a["post_date"])) for a in shown]) + note, ""]

    out += ["## 2. Tables", "",
            f"- {c['tables_expected_headers']:,} tables have the columns "
            + ", ".join(_code(h) for h in EXPECTED_HEADERS),
            f"- {c['tables_other_headers']:,} have other columns (cells are matched by "
            f"header name; a header not in the list above is dropped)",
            f"- {c['rows_cell_count_mismatch']:,} rows have a different number of cells "
            f"than their table has headers (kept: cells matched left to right)",
            f"- {c.get('rows_header_like', 0):,} rows after the header are written in header cells "
            f"(kept as rows)", ""]
    if report["tables"]["header_like_rows"]:
        shown, note = _shown(report["tables"]["header_like_rows"], "rows")
        out += ["### Rows written in header cells", "",
                _md_table(["Article", "Row", "Cells"],
                          [(_link(r["date"]), r["row"], " / ".join(_code(x) for x in r["cells"]))
                           for r in shown]) + note, ""]
    if report["tables"]["other_headers"]:
        shown, note = _shown(report["tables"]["other_headers"], "tables")
        out += ["### Tables with other columns", "",
                _md_table(["Article", "Headers"],
                          [(_link(t["date"]), ", ".join(_code(h) for h in t["headers"]))
                           for t in shown]) + note, ""]
    if report["tables"]["cell_count_mismatch"]:
        shown, note = _shown(report["tables"]["cell_count_mismatch"], "rows")
        out += ["### Rows with a different number of cells", "",
                _md_table(["Article", "Cells"],
                          [(_link(r["date"]), " / ".join(_code(x) for x in r["cells"]))
                           for r in shown]) + note, ""]

    out += ["## 3. Rows", "",
            f"{c['rows']:,} rows in `{TABLE_NAME}`: {c['rows_title']:,} titles (one per "
            f"article, `WordId` ending in `-00`) and {c['rows_table']:,} table rows, with "
            f"{c['rows_distinct_poj']:,} distinct `PojUnicode` and {c['rows_distinct_hanlo']:,} "
            f"distinct `HanLoTaibunPoj` among the table rows.", "",
            _md_table(["Column", "Rows filled"],
                      [(_code(col), f"{c[f'rows_{col}']:,}") for col in COLUMNS]), ""]
    for key, title in [("empty_cells", "Table rows with an empty cell "
                                       "(a title row lacking a heading is listed under Titles)"),
                       ("not_poj", "POJ cells with a piece that is not Pe̍h-ōe-jī"),
                       ("not_kpl", "KIP cells with a piece that is not KPL"),
                       ("multi_tone", "Words with more than one tone mark (input form not built)"),
                       ("caron", "Cells with a caron on a tone-bearing letter")]:
        items = report["rows"][key]
        out += [f"### {title}", "", f"{len(items):,} rows.", ""]
        if not items:
            continue
        shown, note = _shown(items, "rows")
        if key == "empty_cells":
            out += [_md_table(["Article", "Empty", "HanLoTaibunPoj", "PojUnicode", "KipUnicode"],
                              [(_link(r["date"]), ", ".join(r["empty"]), _code(r["HanLoTaibunPoj"]),
                                _code(r["PojUnicode"]), _code(r["KipUnicode"])) for r in shown])]
        elif key in ("not_poj", "not_kpl"):
            out += [_md_table(["Where", "Cell", "Pieces"],
                              [(r["where"], _code(r["text"]),
                                ", ".join(_code(p) for p in r["pieces"])) for r in shown])]
        elif key == "multi_tone":
            out += [_md_table(["Where", "Text", "Words"],
                              [(r["where"], _code(r["text"]),
                                ", ".join(_code(w) for w in r["words"])) for r in shown])]
        else:
            out += [_md_table(["Where", "Text"], [(r["where"], _code(r["text"])) for r in shown])]
        out += [note.strip(), ""] if note else [""]

    out += ["## 4. Counts", "", _md_table(["Count", "Value"],
                                            [(_code(k), f"{v:,}") for k, v in c.items()]), ""]
    return "\n".join(out)


# --- Conversion -------------------------------------------------------------

def convert_articles(tangloo_dir, bunji_dir, report_dir=None, version="", site=None):
    """Reads tangloo_dir (see fetch_articles.py), writes
    bunji_dir/ApodSului.{csv,json} and the report into
    report_dir (default bunji_dir's parent). `site` is what fetch_site /
    read_site returned; read from disk when not given. Returns the counts."""
    tangloo_dir, bunji_dir = Path(tangloo_dir), Path(bunji_dir)
    report_dir = Path(report_dir) if report_dir else bunji_dir.parent
    if site is None:
        site = read_site(tangloo_dir)

    counts = collections.Counter()
    report = {
        "version": version,
        "source": "https://apod.tw/",
        "counts": counts,
        "articles": {"sitemap_only": sorted(set(site["sitemap"]) - site["listing"]),
                     "listing_only": sorted(site["listing"] - set(site["sitemap"])),
                     "missing": site["missing"], "no_heading": [], "no_table": [],
                     "empty_table": [], "titles_incomplete": [], "date_mismatch": []},
        "tables": {"other_headers": [], "cell_count_mismatch": [], "header_like_rows": []},
        "rows": {"empty_cells": [], "not_poj": [], "not_kpl": [], "multi_tone": [], "caron": []},
    }
    counts["articles_sitemap"] = len(site["sitemap"])
    counts["articles_listing"] = len(site["listing"])
    counts["listing_pages"] = site["listing_pages"]
    counts["articles"] = len(set(site["sitemap"]) | site["listing"])
    counts["articles_fetched"] = len(site["fetched"])
    counts["articles_missing"] = len(site["missing"])


    rows, table_rows = [], []
    for date in site["fetched"]:
        url = ARTICLE_URL_TEMPLATE.format(date=date)
        parsed = parse_article((tangloo_dir / "daily" / f"{date}.html").read_text(
            encoding="utf-8", errors="replace"))
        if parsed.post_date and post_date_to_url_date(parsed.post_date) != date:
            report["articles"]["date_mismatch"].append({"date": date, "post_date": parsed.post_date})

        # The title first, as on the page: the article's row 00. The site has
        # no Mandarin title, so its HoaBun stays empty.
        titles = article_titles(parsed)
        # A heading with nothing after its tag (`[KIP]`) is missing too.
        missing_titles = [col for col in TITLE_PREFIXES.values() if not titles.get(col)]
        if missing_titles:
            report["articles"]["titles_incomplete"].append({"date": date, "missing": missing_titles})
            counts["articles_titles_incomplete"] += 1
        title = new_row(date, TITLE_ROW, url)
        # The page's <h1> is the Han-Lo title; it stands in when the heading is missing.
        title["HanLoTaibunPoj"] = titles.get("HanLoTaibunPoj") or parsed.h1 or ""
        for col in ("PojUnicode", "KipUnicode", "EngBun"):
            title[col] = titles.get(col, "")
        if all(not title[col] for col in TITLE_PREFIXES.values()):
            # No heading and no <h1>: a row of empty cells, skipped like a blank
            # table row. The article is under Titles with all four missing.
            counts["rows_blank_skipped"] += 1
        else:
            check_row(title, date, f"{_link(date)} title", report)
            rows.append(title)
            counts["rows_title"] += 1

        table, problem = vocabulary_table(parsed)
        if table is None:
            key = "no_heading" if problem == "no heading" else "no_table"
            report["articles"][key].append(date)
            counts[f"articles_{key}"] += 1
            continue
        counts["articles_with_table"] += 1
        if not table["rows"]:
            report["articles"]["empty_table"].append(date)
            counts["articles_empty_table"] += 1

        headers = table["headers"]
        if headers == EXPECTED_HEADERS:
            counts["tables_expected_headers"] += 1
        else:
            counts["tables_other_headers"] += 1
            report["tables"]["other_headers"].append({"date": date, "headers": headers})
        columns = [HEADER_COLUMNS.get(h) for h in headers]
        for number in table.get("header_like_rows", []):
            counts["rows_header_like"] += 1
            report["tables"]["header_like_rows"].append(
                {"date": date, "row": number, "cells": table["rows"][number - 1]})

        # `number` is the row's position in the site's table, header excluded,
        # so a report entry — and the id — can be found on the page.
        for number, cells in enumerate(table["rows"], 1):
            if len(cells) != len(headers):
                counts["rows_cell_count_mismatch"] += 1
                report["tables"]["cell_count_mismatch"].append({"date": date, "cells": cells})
            row = new_row(date, number, url)
            for col, cell in zip(columns, cells):
                if col:
                    row[col] = cell
            if all(not row[col] for col in HEADER_COLUMNS.values()):
                # A row of empty cells says nothing; a filler line.
                counts["rows_blank_skipped"] += 1
                continue
            empty = [col for col in HEADER_COLUMNS.values() if not row[col]]
            if empty:
                report["rows"]["empty_cells"].append(
                    {"date": date, "empty": empty, "HanLoTaibunPoj": row["HanLoTaibunPoj"],
                     "PojUnicode": row["PojUnicode"], "KipUnicode": row["KipUnicode"]})
            check_row(row, date, f"{_link(date)} row {number}", report)
            rows.append(row)
            table_rows.append(row)
            counts["rows_table"] += 1

    # Unique by construction (one article per date, one position per row); a
    # duplicate would be a bug here, not on the site, and must not be published.
    duplicates = sorted(i for i, n in collections.Counter(r["WordId"] for r in rows).items() if n > 1)
    if duplicates:
        raise ValueError(f"{TABLE_NAME}: WordId not unique: {', '.join(duplicates[:20])}")

    counts["rows"] = len(rows)
    # Distinct vocabulary forms: the titles are sentences, not entries.
    counts["rows_distinct_poj"] = len({r["PojUnicode"] for r in table_rows if r["PojUnicode"]})
    counts["rows_distinct_hanlo"] = len({r["HanLoTaibunPoj"] for r in table_rows if r["HanLoTaibunPoj"]})
    for col in COLUMNS:
        counts[f"rows_{col}"] = sum(1 for r in rows if r[col])
    for key in ("empty_cells", "not_poj", "not_kpl", "caron"):
        counts[f"rows_{key}"] = len(report["rows"][key])
    for key in ("articles_no_heading", "articles_no_table", "articles_empty_table",
                "articles_titles_incomplete", "rows_multi_tone", "rows_title", "rows_table",
                "rows_blank_skipped", "tables_expected_headers", "tables_other_headers",
                "rows_cell_count_mismatch", "rows_header_like", "articles_with_table"):
        counts.setdefault(key, 0)

    dates = site["fetched"]
    report["oldest_article"] = dates[0] if dates else ""
    report["newest_article"] = dates[-1] if dates else ""

    write_csv(rows, COLUMNS, bunji_dir / f"{TABLE_NAME}.csv")
    write_json_rows(rows, bunji_dir / f"{TABLE_NAME}.json")

    report["counts"] = dict(counts)
    write_report(report, report_dir)
    return dict(counts)


def write_report(report, report_dir):
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / f"{REPORT_NAME}.md").write_text(render_report_md(report), encoding="utf-8")
    write_json(report, report_dir / f"{REPORT_NAME}.json")


def set_report_version(report_dir, version):
    """Rewrites the report in report_dir with its version line set — so the
    version directory, named only after conversion succeeded, need not be
    paid for with a second conversion."""
    report_dir = Path(report_dir)
    with open(report_dir / f"{REPORT_NAME}.json", encoding="utf-8") as f:
        report = json.load(f)
    report["version"] = version
    write_report(report, report_dir)


def main():
    parser = argparse.ArgumentParser(description="Convert a downloaded apod.tw into the tables.")
    parser.add_argument("tangloo_dir", help="tangloo/ written by fetch_articles.py")
    parser.add_argument("bunji_dir", help="where to write the tables; the report goes beside it")
    parser.add_argument("--version", default="", help="version id written into the report")
    args = parser.parse_args()
    sys.stdout.reconfigure(errors="backslashreplace")
    counts = convert_articles(args.tangloo_dir, args.bunji_dir, version=args.version)
    for key in ("articles", "articles_with_table", "rows", "rows_title", "rows_table",
                "rows_not_poj", "rows_not_kpl"):
        print(f"{key}: {counts.get(key, 0):,}")


if __name__ == "__main__":
    main()
