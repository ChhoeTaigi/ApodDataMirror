import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

try:
    from convert_articles import (LAIGOAN_MIA, REPORT_NAME, TABLE_NAME, convert_articles,
                                  set_report_version)
    from fetch_articles import SITE, SITEMAP_URL, copy_site, fetch_site, read_site
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent))
    from convert_articles import (LAIGOAN_MIA, REPORT_NAME, TABLE_NAME, convert_articles,
                                  set_report_version)
    from fetch_articles import SITE, SITEMAP_URL, copy_site, fetch_site, read_site

# The published table, CSV and JSON, is what change detection compares: a
# new version appears only when the vocabulary (or how this repo renders it)
# actually changed, not when the site's templates do. The report is not
# compared: a report-only change goes live with the next table change.
CHANGE_KEYS = [f"bunji/{TABLE_NAME}.{ext}" for ext in ("csv", "json")]

# A partial failure upstream — a site redesign that renames the 詞彙學習
# heading or the title headings, a sitemap cut short — shows up as a sharp
# drop in these counts against the last version. Losing more than
# MAX_COUNT_DROP of any refuses to publish, unless --force. The table rows are
# watched on their own (every article has a title row, table or not), and the
# filled POJ/KIP counts catch titles that lost their headings.
WATCHED_COUNTS = ["articles", "articles_with_table", "rows_table",
                  "rows_PojUnicode", "rows_KipUnicode"]
MAX_COUNT_DROP = 0.05

# The site's terms, from https://apod.tw/faq/: open data from the site is
# welcome for educational, non-commercial, public use, with attribution.
LICENSE = "apod.tw FAQ: educational, non-commercial, public use, with attribution"
ATTRIBUTION = LAIGOAN_MIA

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DIR = BASE_DIR / "public"
MANIFEST_FILE = PUBLIC_DIR / "manifest.json"
# A refused run leaves the report it built here, to be read before --force.
# Gitignored, like every public/temp_update_*.
FAILED_DIR = PUBLIC_DIR / "temp_update_failed"
README_FILE = BASE_DIR / "README.md"
INDEX_FILE = BASE_DIR / "index.md"


def verify_docs_in_sync():
    """README.md and index.md must be byte-identical — a rule in every sibling
    mirror. Checked before any network work so a drift is cheap to fix."""
    if not README_FILE.exists() or not INDEX_FILE.exists():
        print("ERROR: both README.md and index.md must exist.")
        return False
    if README_FILE.read_bytes() != INDEX_FILE.read_bytes():
        print("ERROR: README.md and index.md have drifted apart.")
        print("       They must stay byte-identical. Fix with:")
        print("           cp README.md index.md")
        return False
    return True


def reserve_timestamp_dir():
    """Creates and returns a new, empty version directory named by the current
    second. Creating it is the reservation: two runs in the same second (or a
    clock stepped back) can no longer pick the same name."""
    while True:
        path = PUBLIC_DIR / datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        try:
            path.mkdir()
            return path
        except FileExistsError:
            time.sleep(1)


def calculate_file_hash(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def hash_published(version_dir):
    """{path relative to version_dir: sha256} for everything except tangloo/."""
    hashes = {}
    for path in sorted(version_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(version_dir)
        if rel.parts[0] == "tangloo":
            continue
        hashes[rel.as_posix()] = calculate_file_hash(path)
    return hashes


def load_manifest():
    if MANIFEST_FILE.exists():
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_manifest(data):
    # Write to a temp file and atomically rename so a crash mid-write can't
    # leave a half-written manifest that breaks every subsequent run.
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    tmp = MANIFEST_FILE.with_suffix(MANIFEST_FILE.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, MANIFEST_FILE)


def keep_report(staging):
    """A refused run's report goes to FAILED_DIR/report/, replacing an older
    one: the refusal is judged by it."""
    built = sorted(staging.glob(f"{REPORT_NAME}.*"))
    if not built:
        return False
    shutil.rmtree(FAILED_DIR / "report", ignore_errors=True)
    (FAILED_DIR / "report").mkdir(parents=True)
    for path in built:
        os.replace(path, FAILED_DIR / "report" / path.name)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Mirror the 詞彙學習 vocabulary of every apod.tw article."
    )
    parser.add_argument(
        "--tangloo",
        metavar="DIR",
        help="Use a kept download (a published version's tangloo/, written by "
             "fetch_articles.py) instead of fetching the site.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Create a new version directory even when the tables are "
             "unchanged, and publish even when counts fell sharply since the "
             "last version or the newest article is older than the published one.",
    )
    args = parser.parse_args()
    # Titles and arrows must not crash a run on a terminal that is not UTF-8.
    sys.stdout.reconfigure(errors="backslashreplace")

    print("Starting update check...")

    if not verify_docs_in_sync():
        sys.exit(1)
    print("README.md and index.md are in sync.")

    current_manifest = load_manifest()
    latest_version_dir_name = current_manifest.get("latest_version_dir")

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix="temp_update_", dir=str(PUBLIC_DIR)))

    target_dir = None
    refused = False
    success = False
    try:
        # 1. Fetch the site into temp (or take the kept download).
        tangloo = temp_dir / "tangloo"
        if args.tangloo:
            source = Path(args.tangloo).resolve()
            copy_site(source, tangloo)
            site = read_site(tangloo)
            print(f"Using kept download: {source}")
        else:
            site = fetch_site(tangloo)
        newest = site["fetched"][-1] if site["fetched"] else ""
        oldest = site["fetched"][0] if site["fetched"] else ""
        lastmod = max(site["sitemap"].values(), default="")
        print(f"Articles {oldest} to {newest}; sitemap lastmod {lastmod}")

        # Publishing an older download would quietly drop every article since.
        published_newest = current_manifest.get("newest_article")
        if newest and published_newest and newest < published_newest and not args.force:
            print(f"ERROR: newest article {newest} is older than {published_newest}, which "
                  f"{latest_version_dir_name} was built from. Rerun with --force to "
                  "publish it anyway.")
            sys.exit(1)

        # 2. Build into a staging version dir inside temp. Nothing under
        #    public/ is touched until conversion succeeded.
        staging = temp_dir / "version"
        stats = convert_articles(tangloo, staging / "bunji", report_dir=staging,
                                 version="(unpublished)", site=site)
        if stats["rows"] == 0:
            print("Kept 0 rows — refusing to publish an empty mirror. Aborting.")
            refused = True
            sys.exit(1)
        previous = current_manifest.get("counts", {})
        drops = [f"{key}: {previous[key]:,} → {stats.get(key, 0):,}"
                 for key in WATCHED_COUNTS
                 if previous.get(key) and stats.get(key, 0) < previous[key] * (1 - MAX_COUNT_DROP)]
        if drops and not args.force:
            print(f"Counts fell by more than {MAX_COUNT_DROP:.0%} since {latest_version_dir_name}:")
            for drop in drops:
                print(f"  {drop}")
            print("Refusing to publish. Rerun with --force if the drop is real.")
            refused = True
            sys.exit(1)

        new_hashes = hash_published(staging)
        cached_hashes = current_manifest.get("files", {})

        # 3. Change detection on the *published* tables.
        existing_dir = PUBLIC_DIR / latest_version_dir_name if latest_version_dir_name else None
        changed = (args.force
                   or not cached_hashes
                   or any(new_hashes.get(k) != cached_hashes.get(k) for k in CHANGE_KEYS)
                   or existing_dir is None
                   or not existing_dir.exists())

        now = datetime.datetime.now().isoformat()
        if not changed:
            print(f"No changes in {', '.join(CHANGE_KEYS)}. Keeping {latest_version_dir_name}.")
            # Record that the mirror was checked against the site.
            new_manifest = dict(current_manifest)
            new_manifest["last_checked"] = now
            # Never moved back (--force with an older download).
            new_manifest["last_checked_newest_article"] = max(
                newest, current_manifest.get("last_checked_newest_article") or "")
            save_manifest(new_manifest)
            success = True
            target_dir = existing_dir
        else:
            print("Changes detected (or --force). Creating a new version directory...")
            target_dir = reserve_timestamp_dir()
            # The report names the version it belongs to; only the report is
            # rewritten, the tables (and the stats) are the ones already built.
            set_report_version(staging, target_dir.name)
            new_hashes = hash_published(staging)
            for item in staging.iterdir():
                shutil.move(str(item), str(target_dir / item.name))
            # tangloo/ keeps the downloaded pages beside the tables they
            # produced. Gitignored: it is what was downloaded, not what this
            # repo publishes.
            shutil.move(str(tangloo), str(target_dir / "tangloo"))

            new_manifest = {
                "last_updated": now,
                "last_checked": now,
                "last_checked_newest_article": max(
                    newest, current_manifest.get("last_checked_newest_article") or ""),
                "latest_version_dir": target_dir.name,
                "source": SITE,
                "source_sitemap": SITEMAP_URL,
                "source_sitemap_lastmod": lastmod,
                "oldest_article": oldest,
                "newest_article": newest,
                "fetched_at": site.get("fetched_at"),
                "license": LICENSE,
                "attribution": ATTRIBUTION,
                "row_count": stats["rows"],
                "article_count": stats["articles_fetched"],
                "files": new_hashes,
                "counts": stats,
            }
            save_manifest(new_manifest)
            # Published: from here on, a failure must not remove target_dir.
            success = True
            print(f"Created {target_dir} and updated manifest.json.")

        if FAILED_DIR.exists():
            shutil.rmtree(FAILED_DIR)
    finally:
        if not success and target_dir and target_dir.exists() \
                and target_dir.name != latest_version_dir_name:
            print(f"Removing partial target directory: {target_dir}")
            shutil.rmtree(target_dir)
        if temp_dir.exists():
            if refused and keep_report(temp_dir / "version"):
                print(f"\nThe report this run built is in {FAILED_DIR / 'report'} "
                      "— read it before rerunning with --force.")
            shutil.rmtree(temp_dir)

    print("\nUpdate complete!")
    if target_dir:
        print(f"Data stored in: {target_dir}")


if __name__ == "__main__":
    main()
