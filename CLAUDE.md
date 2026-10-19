# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Data mirror of the 詞彙學習 (vocabulary) tables of 逐工一幅天文圖 (https://apod.tw/), the Taigi translation of NASA's Astronomy Picture of the Day. Part of the ChhoeTaigi project, built on the same layout as `WiktionaryTaioanoeDataMirror` and `WikipediaPehoejiDataMirror`. The repo fetches every daily article (`https://apod.tw/daily/YYYYMMDD/`), reads the table after each article's `詞彙學習` heading (columns 漢羅, POJ, KIP, 華語, English) and the article's four title headings, and publishes one CSV+JSON table, `ApodSului`, with the ChhoeTaigi database's column names: each article's title as a row, then its table rows. Hosted via GitHub Pages.

Licence: apod.tw's FAQ welcomes its Taigi text as open data for educational, non-commercial, public use with attribution (`逐工一幅天文圖 https://apod.tw`); the translations belong to their translators. Not a Creative Commons licence — quote the FAQ, do not call it CC.

It replaces `../WebFetchApodTw` (Kotlin + jsoup, run once on 2025-06-27, `apod_tw_vocabulary_20250627.csv`, 13,030 rows). That run's output is the regression reference: of its 1,448 articles still on the site, 1,446 match this mirror row for row; the other two (20210823, 20211117) had every row twice there — a concurrency bug in the Kotlin — and 63 articles were missing from it altogether. Its `DictWordID` scheme (`APODTW-YYYYMMDD-NNN`) is not reproduced: `DictWordID` and `SuBe` are assigned by the database. This mirror's own id is `WordId` (`YYYYMMDD-NN`; `00` is the article's title row).

## Commands

```bash
# Full update: fetch the sitemap, the /daily/ listing and every article
# (~1,500 pages, a few minutes), convert, publish a version if a table changed
cd script && python update_data.py

# Rebuild from a kept download (a published version's tangloo/), no network
cd script && python update_data.py --tangloo ../public/{version}/tangloo

# Force a new version even when the tables are unchanged, and publish even
# when counts fell more than 5% or the newest article is older than published
cd script && python update_data.py --force

# Conversion only, into any directory
cd script && python convert_articles.py ../public/{version}/tangloo /tmp/out/bunji --version test

# Download only
cd script && python fetch_articles.py /tmp/tangloo
```

Dependencies: pure Python 3 stdlib. Conversion takes ~5 s; the download a few minutes.

### Verifying a change

There is no test suite. The pipeline *is* the check: run it (with `--tangloo` against the published version's download while iterating) and read `public/{version}/ApodDataQuality.md`.

- **Section 1** must say sitemap, listing and union agree (1,511 in the first version, every one with a table). Articles with no heading or no table: 0. A change here means the site changed, not the code — look at the pages.
- **Section 2**: every table has the five expected headers; cell-count mismatches 0.
- **Row checks.** 20190411 row 1 is `20190411-01`, after its title row `20190411-00` (`Te-it-ê o͘-tōng sī-pêng-sòaⁿ kui-bô͘ ê iáⁿ-siōng`, `HoaBun` empty): `sū-kiāⁿ-sī-pêng-sòaⁿ` / `su7-kiann7-si7-peng5-soann3` / `sū-kiānn-sī-pîng-suànn` / `su7-kiann7-si7-ping5-suann3` / `事件視平線` / `事件視界` / `event horizon`. 20250613 row 3: `UGC jī-pat-pat-ngó͘` → `UGC ji7-pat-pat-ngoo2`. 20211117 has 7 table rows, 20210823 has 5. Title rows: 20240527 has no `[漢羅]` heading and takes its `<h1>`; 20210324 and 20210330 write `[English]` as a link and must still get `EngBun`; 20211216 has `[KIP]Lâm-hong` (no space) and must still get `KipUnicode`; 20220211's `[KIP]` is empty, so its title row has an empty `KipUnicode` and it is listed under Titles (7 articles).
- **Section 3**: 15,098 rows = 1,511 titles + 13,587 table rows; the distinct counts (4,943 `PojUnicode`, 4,091 `HanLoTaibunPoj`) are over table rows only. "POJ cells with a piece that is not Pe̍h-ōe-jī" ~17 (8 of them titles), "KIP cells with a piece that is not KPL" ~94 (20 titles) — all genuine slips on the site (KPL in the POJ column and vice versa, a Han character in a reading, a tone mark on a catalogue letter: `Ḿ7`); each entry says `title` or `row N`. Carons 4. Multi-tone words 0. If a change makes these numbers jump, the check got looser or stricter, not the data.
- A second run with unchanged data must reuse the existing version directory.

## Architecture

### Data Pipeline (`script/`)

1. **`update_data.py`** — Main entry point. Verifies `README.md`/`index.md` are in sync, fetches the site into a temp dir (or copies a `--tangloo` download), converts into a staging directory, refuses to publish a >5% drop in `WATCHED_COUNTS` (articles, tables, table rows, and the filled POJ/KIP counts — the last so a changed title-heading format is caught too) or a newest article older than the published one (unless `--force`), compares the SHA256 of the published table (CSV and JSON) against `public/manifest.json`, and only then reserves a timestamped version directory, rewrites the report with its name (`set_report_version`, no second conversion), moves the staging dir into it and writes the manifest. Same shape as the Wiktionary mirror's, with the download stage replaced by `fetch_site`.

2. **`fetch_articles.py`** — `fetch_site(tangloo_dir)`: downloads `sitemap.xml`, walks `/daily/`, `/daily/page/N/` until a 404, fetches the union of the two article sets with 4 threads and a pause, and writes `fetch.json` last (what it learned; its presence marks a complete download). `read_site` reads a kept download back; `copy_site` hard-links one into a run. 404 is an answer (`missing`); anything else after retries raises `FetchError`, which aborts the run at once — the queued articles are cancelled (`shutdown(cancel_futures=True)`), not each tried and timed out. `Retry-After` is honoured in both its forms, seconds and HTTP date.

3. **`convert_articles.py`** — `ArticleParser` (stdlib `html.parser`) collects `<h1>`, `p.post_date`, every `<h2>` and every `<table>` in document order; `vocabulary_table` takes the first table after the `詞彙學習` heading and before the next; `article_titles` reads the `[漢羅]`/`[POJ]`/`[KIP]`/`[English]` headings into the article's title row (`TITLE_ROW`, id suffix `00`), written before its table rows; every row, title or table, gets its id and source columns from `new_row` and its `PojInput`/`KipInput` and spelling checks from `check_row`; the report is rendered to Markdown and JSON. Nothing is corrected.

4. **`poj_text.py`** — Copied byte-for-byte from `WiktionaryTaioanoeDataMirror/script/poj_text.py` (`diff` must be empty; its docstring still speaks of the Wikimedia mirrors, and that is fine). Used here: `poj_unicode_to_input`, `POJ_SYLLABLE`, `READING_SPLIT`, `TONE_MARKS`, `_clusters`, `_has_caron_on_bearer`. The same conversion serves the KPL columns: KPL uses the same tone diacritics and writes `oo`/`nn` as plain letters already. Do not edit here: change the sibling and copy, so the three mirrors convert identically.

### Key design decisions

- **Two enumerations, one fetch.** The sitemap alone would do, but a sitemap cut short would silently shrink the mirror. The listing is walked too, the union is fetched, and the difference is reported. The 5% count-drop refusal is the second guard.

- **One row per table row, not per term.** `銀河系` appears in dozens of articles. Merging would lose which article taught the term and would need a rule for rows whose other columns differ. The database can group by `PojUnicode` itself.

- **Database column names.** `PojUnicode`, `PojInput`, `KipUnicode`, `KipInput`, `HanLoTaibunPoj`, `HoaBun`, `EngBun`, `LaigoanMia`, `LaigoanBangchi` — so the CSV loads without renaming — after the mirror's own id column `WordId`. `LaigoanMia` is the constant `逐工一幅天文圖 https://apod.tw` (`LAIGOAN_MIA`), the attribution line the FAQ asks for; the manifest's `attribution` is the same constant. The site's single 漢羅 column goes to `HanLoTaibunPoj` only; its Roman parts follow whichever orthography the translator used (mostly neutral: `ê`, `kah`, names).

- **Ids name positions.** `WordId` is `{date}-{NN}` (`WORD_ID`): the article's URL date and a two-digit number — `00` (`TITLE_ROW`) for the title, then the row's position in the site's table, the same number as the report's `row N` (the largest table has 25 rows; a hundredth row would simply get three digits). Unique by construction — one article per date, one position per row — and `convert_articles` raises, naming the duplicates, if not, since a duplicate would be a bug here. An id is stable only while the site does not insert or remove a row above it; the database keeps its own `DictWordID`.

- **Cells matched by header name, not position.** `HEADER_COLUMNS` maps the site's headers; a reordered table still loads, an unknown header is dropped and listed, a row with a different cell count is listed and kept left-to-right. All 1,511 tables have had the same five headers, so none of this has fired.

- **The title is a row, not a table.** The four title headings are Taigi text in the table's languages minus Mandarin, so they are the article's row `00` of `ApodSului`, with `HoaBun` empty, and go through the same spelling checks. An earlier draft kept them in a second table, `ApodBunchiunn` (one row per article with the date and a row count); it was dropped because it held no data of its own — the date is in every id and link, the count is a group-by. A title with none of the four headings and no `<h1>` is skipped like a blank table row (`rows_blank_skipped`; none so far). The page's `post_date` (`13. June 2025`) is parsed only to check it agrees with the URL date (reported if not).

- **The spelling checks are a report, not a filter.** `pieces_not_poj`/`pieces_not_kpl` test only pieces that carry an orthography marker (a tone mark; `o͘`/`ⁿ` for POJ; `oo`/`nn`/`ts` for KPL), skip capitalised tone-less pieces (names: `Kennedy`, `Bennu`), split on punctuation as well as spaces and hyphens (`7293：Kńg`, where the site put no space after the colon, tests `Kńg`), match in NFC (the shared regex is written with precomposed letters; the cell itself is published as written), and accept the tone-9 marks the shared `POJ_SYLLABLE` regex does not know (`iăn-jín`; `TONE_9` is derived from `TONE_MARKS`). `KPL_SYLLABLE` is a local approximation (initials, rhymes with `oo`/`nn`/`ir`/`er`, codas) — good enough to catch POJ in the KIP column, which is what it is for.

- **Change detection, staging, count-drop refusal** — as in the siblings: the four tables' hashes decide, nothing under `public/` is touched until conversion succeeded, a refused run keeps its report in `public/temp_update_failed/report/`.

### Non-obvious invariants

- **`TITLE_LINE` is `^\[?(漢羅|POJ|KIP|English)\]?\s*(.*)$`.** The site has headings with the tag as a Markdown link (`English Aurorae…`, no brackets), with no space after the tag (`[KIP]Lâm-hong`), and with nothing after it (`[KIP]`). An empty match is an empty title, counted as missing in the report; `setdefault` keeps the first heading of each kind.

- **The `<h1>` stands in for a missing `[漢羅]` heading** (20240527), never for the other three: the h1 is the Han-Lo title by construction.

- **`ArticleParser` treats a row of `<th>` cells as the header even outside `<thead>`**, but only the first one: a later header-like row (a sub-heading, an entry typed in `<th>` cells) is kept as a data row and listed in the report under "Rows written in header cells" (`header_like_rows`), so nothing drops out of the table silently. Hugo renders `<thead>`, but a hand-written table might not.

- **Report locations count the site's rows.** `row N` in the report is the row's position in the article's table, header excluded, blank filler rows included, so it can be found on the page; `WordId` carries the same number, so a skipped blank row leaves a gap in that article's ids (`rows_blank_skipped`, 0 so far).

- **Whitespace is collapsed per cell, including NBSP and ideographic space**; `<br>` becomes a space. Cell text is not otherwise normalised (no NFC): a stacked `mo̍͘h` is published as the site has it and flagged in the report.

- **`fetch.json` is written last.** `read_site` trusts it; a tangloo/ without one (an aborted run) is read from disk and cannot tell a 404 from an unfetched page — which is why `--tangloo` is documented for a published version's download only.

- **`newest_article` only moves forward** (`last_checked_newest_article`), like the Wiktionary mirror's dump date; `--force` can publish an older download but not rewind the check.

### Downstream

`ChhoeTaigiDatasetGenerator` has no mapper for this source yet (the 2025 Kotlin CSV was never loaded). The intended follow-up is a mapper reading `bunji/ApodSului.csv` as is: every column after `WordId`, `LaigoanMia` and `LaigoanBangchi` included, is already in database form; `WordId` is the mirror's own id, for the mapper to map to `DictWordID` or drop. Title rows are the ones whose `WordId` ends in `-00`; the mapper decides whether to load them.

### Data Layout (`public/`)

```
public/
  manifest.json                   # Latest version, source, newest article, per-file SHA256, counts
  {YYYYMMDD-HHMMSS}/              # Timestamped version directory
    ApodDataQuality.md            # Data-quality report
    ApodDataQuality.json          # Same, machine-readable, with the full lists
    bunji/
      ApodSului.csv/.json         # one row per article title (id suffix 00) and per vocabulary entry
    tangloo/                      # The download — gitignored
      sitemap.xml
      listing/page-N.html
      daily/YYYYMMDD.html
      fetch.json
```

### Hosting

- `index.md` is the GitHub Pages landing page (Pages serves branch `main`, path `/`)
- `.nojekyll` disables Jekyll processing

## Important Rules

- **`README.md` and `index.md` must stay in sync.** They have identical content. `update_data.py` aborts before any network work if they differ. Fix with `cp README.md index.md`. Update the version ID, dates and counts in both after each new version.
- **`manifest.json` keys files by path relative to the version directory** (`bunji/ApodSului.csv`), skipping `tangloo/`.
- **Never commit the download.** `public/*/tangloo/` is gitignored.
- **Never correct a cell silently.** Everything is published as written; what looks wrong goes in the report.
- **Be a polite client.** `WORKERS = 4`, `PAUSE_SECONDS = 0.25`, a descriptive `User-Agent`, retries that honour `Retry-After`. Do not raise the parallelism; the whole site is ~1,500 small pages.
- **Pure stdlib only.**

## Terminology (Taigi)

- **Taigi** — the language. Never "Taiwanese Southern Min", "Holo" or "Hokkien" in prose.
- **Roman Orthography** — never "Romanization".
- **Pe̍h-ōe-jī (POJ)** — the Taigi Roman-script Orthography. The site's `POJ` column.
- **KPL (Kàu-io̍k Pō͘ Lô-má-jī)** — the Taigi Latin-script Orthography. The site's `KIP` column; never "Tâi-lô" or "TL" in prose (`KIP` only as the site's own header and in the column names `KipUnicode`/`KipInput`).
- **Hàn-jī** (漢字) — Chinese characters; **Hàn-Lô** (漢羅) — mixed Han and Roman writing. Column `HanLoTaibunPoj`.
- **sû-lūi** (詞彙) — vocabulary. Table `ApodSului`; `WordId` its row id.
- **bûn-chiuⁿ** (文章) — article. Its title is its row `00` in `ApodSului`; there is no article table.
- **ji̍t-kî** (日期) — date. The `YYYYMMDD` of every article URL and `WordId`.
- **bûn-jī** (文字) — text data. Directory `bunji/`.
- **táng-ló͘** (檔路) — download. Directory `tangloo/`.
- **Hôa-bûn, Eng-bûn** (華文, 英文) — Mandarin, English. Columns `HoaBun`, `EngBun`.
- **lâi-goân** (來源) — source. Columns `LaigoanMia` (來源名, its name) and `LaigoanBangchi` (來源網址, its link).
