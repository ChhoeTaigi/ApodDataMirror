"""Download the apod.tw pages this mirror reads.

apod.tw (逐工一幅天文圖, the Taigi translation of NASA's Astronomy Picture of
the Day) is a static site with no API. Every daily article has a URL of the
form `https://apod.tw/daily/YYYYMMDD/`. The articles are enumerated from two
places and the union is fetched:

- `sitemap.xml`, which lists every page of the site with a `lastmod`;
- the paginated listing `/daily/`, `/daily/page/2/`, … until a 404.

Either alone would do; reading both makes a truncated sitemap or a broken
listing visible in the report instead of silently shrinking the mirror.

Layout written under tangloo_dir (檔路, the download):

    sitemap.xml
    listing/page-N.html        # N from 1 (= /daily/)
    daily/YYYYMMDD.html        # one file per article, as served

The function returns what it learned; nothing is parsed here beyond the
article links (see convert_articles.py for the content).
"""
import concurrent.futures
import datetime
import email.utils
import json
import re
import shutil
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

SITE = "https://apod.tw"
SITEMAP_URL = f"{SITE}/sitemap.xml"
LISTING_URL = f"{SITE}/daily/"
LISTING_PAGE_URL = f"{SITE}/daily/page/{{n}}/"
ARTICLE_URL_TEMPLATE = f"{SITE}/daily/{{date}}/"
ARTICLE_LINK = re.compile(r"https://apod\.tw/daily/(\d{8})/")
# The sitemap gives each article's lastmod — its publication date, in
# practice — and the newest one dates the download.
SITEMAP_ENTRY = re.compile(
    r"<loc>https://apod\.tw/daily/(\d{8})/</loc>\s*<lastmod>([^<]*)</lastmod>")

USER_AGENT = "ChhoeTaigi-ApodDataMirror/1.0 (https://github.com/ChhoeTaigi)"
HTTP_TIMEOUT = 60
# apod.tw sits behind Cloudflare; a few polite parallel connections with a
# pause between requests have never been throttled. Keep it that way.
WORKERS = 4
PAUSE_SECONDS = 0.25
RETRIES = 4
RETRY_BACKOFF_SECONDS = 3
# A 429/503 is retried after its Retry-After, up to this.
RETRY_AFTER_MAX_SECONDS = 120
# The listing is walked until a page answers 404; this is a safety stop.
MAX_LISTING_PAGES = 200
# What fetch_site learned, kept beside the pages (see read_site).
FETCH_RECORD = "fetch.json"


class FetchError(RuntimeError):
    """A page that could not be fetched after RETRIES tries — a network
    error, a 5xx, a challenge page. Never a 404: that is an answer."""


class NotFound(Exception):
    pass


def _open(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(req, timeout=HTTP_TIMEOUT)


def _retry_after_seconds(value):
    """Retry-After as seconds: a delay (`120`) or an HTTP date (`Wed, 10 Oct
    2026 07:05:00 GMT`), both allowed by RFC 7231; None when unreadable."""
    value = (value or "").strip()
    if value.isdigit():
        return int(value)
    try:
        when = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when is None:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=datetime.timezone.utc)
    return max(0, (when - datetime.datetime.now(datetime.timezone.utc)).total_seconds())


def _retry_wait(error, attempt):
    wait = RETRY_BACKOFF_SECONDS * attempt
    retry_after = _retry_after_seconds((getattr(error, "headers", None) or {}).get("Retry-After"))
    if retry_after is not None:
        wait = max(wait, min(retry_after, RETRY_AFTER_MAX_SECONDS))
    return wait


def fetch(url):
    """The body of url as bytes. Raises NotFound on a 404 and FetchError when
    RETRIES attempts all failed. A body shorter than its Content-Length is a
    failure, not a page."""
    last_error = None
    for attempt in range(1, RETRIES + 1):
        try:
            with _open(url) as r:
                body = r.read()
                expected = r.getheader("Content-Length") or ""
            if expected.isdigit() and len(body) != int(expected):
                raise OSError(f"got {len(body):,} of {int(expected):,} bytes")
            return body
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise NotFound(url) from None
            last_error = e
        except Exception as e:
            last_error = e
        if attempt < RETRIES:
            time.sleep(_retry_wait(last_error, attempt))
    raise FetchError(f"giving up on {url} after {RETRIES} attempts: {last_error}")


def sitemap_articles(sitemap_text):
    """{date: lastmod} of the daily articles in the sitemap."""
    return {date: lastmod for date, lastmod in SITEMAP_ENTRY.findall(sitemap_text)}


def listing_articles(listing_html):
    return set(ARTICLE_LINK.findall(listing_html))


def fetch_site(tangloo_dir, log=print):
    """Downloads the sitemap, the listing pages and every article into
    tangloo_dir. Returns a dict with what was found:

        sitemap:  {date: lastmod}
        listing:  {date} across all listing pages
        listing_pages: how many listing pages there were
        fetched:  sorted dates whose article was downloaded
        missing:  sorted dates that answered 404

    Raises FetchError when a page could not be fetched: a partial download
    must not become a version."""
    tangloo_dir = Path(tangloo_dir)
    (tangloo_dir / "listing").mkdir(parents=True, exist_ok=True)
    (tangloo_dir / "daily").mkdir(parents=True, exist_ok=True)

    log(f"Fetching {SITEMAP_URL}...")
    sitemap = fetch(SITEMAP_URL)
    (tangloo_dir / "sitemap.xml").write_bytes(sitemap)
    in_sitemap = sitemap_articles(sitemap.decode("utf-8", "replace"))
    log(f"  {len(in_sitemap):,} articles in the sitemap")

    in_listing = set()
    pages = 0
    for n in range(1, MAX_LISTING_PAGES + 1):
        url = LISTING_URL if n == 1 else LISTING_PAGE_URL.format(n=n)
        try:
            body = fetch(url)
        except NotFound:
            break
        pages = n
        (tangloo_dir / "listing" / f"page-{n}.html").write_bytes(body)
        found = listing_articles(body.decode("utf-8", "replace"))
        if not found:
            # A listing page without a single article link is the end too.
            break
        in_listing |= found
        time.sleep(PAUSE_SECONDS)
    log(f"  {len(in_listing):,} articles on {pages} listing pages")

    dates = sorted(set(in_sitemap) | in_listing)
    log(f"Fetching {len(dates):,} articles with {WORKERS} workers...")
    fetched, missing = [], []
    lock = threading.Lock()
    done = 0

    def one(date):
        nonlocal done
        url = ARTICLE_URL_TEMPLATE.format(date=date)
        try:
            body = fetch(url)
        except NotFound:
            with lock:
                missing.append(date)
            return
        finally:
            time.sleep(PAUSE_SECONDS)
        target = tangloo_dir / "daily" / f"{date}.html"
        part = target.with_name(target.name + ".part")
        part.write_bytes(body)
        part.replace(target)
        with lock:
            fetched.append(date)
            done += 1
            if done % 100 == 0:
                log(f"  {done:,} / {len(dates):,}")

    pool = concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS)
    try:
        futures = [pool.submit(one, d) for d in dates]
        # The first FetchError aborts the run; the articles still queued are
        # cancelled rather than each tried (and timed out) in turn.
        for future in concurrent.futures.as_completed(futures):
            future.result()
    except BaseException:
        pool.shutdown(wait=True, cancel_futures=True)
        raise
    pool.shutdown(wait=True)
    log(f"  fetched {len(fetched):,}, 404 for {len(missing):,}")

    found = {
        "sitemap": in_sitemap,
        "listing": sorted(in_listing),
        "listing_pages": pages,
        "fetched": sorted(fetched),
        "missing": sorted(missing),
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    # Written last: its presence says the download is complete, and read_site
    # takes `missing` from it instead of guessing from what is on disk.
    with open(tangloo_dir / FETCH_RECORD, "w", encoding="utf-8") as f:
        json.dump(found, f, ensure_ascii=False, indent=1)
        f.write("\n")
    found["listing"] = in_listing
    return found


def read_site(tangloo_dir):
    """What fetch_site learned, re-read from a kept tangloo_dir (no network).
    With its fetch.json (written by a completed fetch_site) that is exact.
    Without it the sitemap and listing pages are parsed again, `fetched` is
    what is on disk and `missing` is what the sitemap or listing names but no
    file holds — an aborted download cannot be told from a 404 then."""
    tangloo_dir = Path(tangloo_dir)
    record = tangloo_dir / FETCH_RECORD
    if record.is_file():
        with open(record, encoding="utf-8") as f:
            found = json.load(f)
        found["listing"] = set(found["listing"])
        absent = [d for d in found["fetched"] if not (tangloo_dir / "daily" / f"{d}.html").is_file()]
        if absent:
            raise FileNotFoundError(f"{len(absent)} article files named in {record} are missing, "
                                    f"e.g. daily/{absent[0]}.html")
        return found
    sitemap_file = tangloo_dir / "sitemap.xml"
    if not sitemap_file.is_file():
        raise FileNotFoundError(f"{sitemap_file} is missing")
    in_sitemap = sitemap_articles(sitemap_file.read_text(encoding="utf-8", errors="replace"))
    in_listing = set()
    pages = sorted(tangloo_dir.glob("listing/page-*.html"),
                   key=lambda p: int(p.stem.split("-")[1]))
    for page in pages:
        in_listing |= listing_articles(page.read_text(encoding="utf-8", errors="replace"))
    on_disk = {p.stem for p in (tangloo_dir / "daily").glob("*.html")}
    dates = set(in_sitemap) | in_listing
    return {
        "sitemap": in_sitemap,
        "listing": in_listing,
        "listing_pages": len(pages),
        "fetched": sorted(dates & on_disk),
        "missing": sorted(dates - on_disk),
    }


def copy_site(source_dir, target_dir):
    """Copies a tangloo/ directory (hard links where possible)."""
    source_dir, target_dir = Path(source_dir), Path(target_dir)
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or path.name.endswith(".part"):
            continue
        target = target_dir / path.relative_to(source_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            target.hardlink_to(path)
        except OSError:
            shutil.copy2(path, target)


if __name__ == "__main__":
    import sys
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tangloo")
    found = fetch_site(out)
    print(f"sitemap {len(found['sitemap']):,}, listing {len(found['listing']):,} "
          f"on {found['listing_pages']} pages, fetched {len(found['fetched']):,}, "
          f"missing {len(found['missing']):,}")
