#!/usr/bin/env python3
"""Check the invariants this list promises, so a drift fails loudly instead of quietly.

    python3 scripts/check_consistency.py          # structure only, no network
    python3 scripts/check_consistency.py --links  # also resolve every URL

Six checks, each one a defect found in a comparable list rather than a
hypothetical: a table of contents whose anchors no longer resolve, an entry
listed twice, two language versions that have drifted apart, a heading that
carries an emoji and so breaks the anchor a hand-written link points at, a
file that nothing links to, and a project-page explorer generated from an
older README. Exit status is non-zero if any check fails.
"""

import argparse
import collections
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
READMES = ["README.md", "README_zh.md"]
DOCS = ["docs/reported-evidence.md", "docs/evidence-criteria.md", "CONTRIBUTING.md"]
# Listed once is the rule; Theory's mapping is the declared exception, and a
# shared repository is a fact about the two works rather than a mistake.
ENTRY_EXEMPT = {"SkillForge"}

ENTRY = re.compile(r"^- \*\*(.+?)\*\*")
LINK = re.compile(r"\[\[(\w+)\]\]\((https?://[^)]+)\)")
HEADING = re.compile(r"^(#{2,4}) (.+)$", re.M)
ANCHOR_TAG = re.compile(r'<a id="([^"]+)"></a>')
ANCHOR_REF = re.compile(r"\]\(#([^)]+)\)")
FILE_REF = re.compile(r"\]\((?!https?://|#)([^)#]+)(?:#[^)]*)?\)")


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return handle.read()


def slug(text):
    """GitHub's heading slug, close enough for the cases this list uses."""
    text = re.sub(r"<[^>]+>", "", text).lower().replace(" ", "-")
    return re.sub(r"[^a-z0-9一-鿿\-_]", "", text)


def entry_lines(text):
    """Yield (name, links) once per entry line, outside fenced blocks.

    An entry is a bulleted line that names a work and links to it. Bullets that
    only explain something, such as the ones inside the scope-exclusion block,
    carry no link and are not entries; neither is the fenced format example,
    whose placeholder reads `(url)` rather than a real address.
    """
    fenced = False
    for line in text.split("\n"):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        match = ENTRY.match(line)
        links = LINK.findall(line)
        if match and links:
            yield match.group(1), links


def entries(text):
    """Entry name -> the set of (kind, url) links across its occurrences."""
    found = collections.defaultdict(set)
    for name, links in entry_lines(text):
        found[name].update(links)
    return found


def strip_code(text):
    """Drop fenced blocks and inline code, so a link written as an example of
    the format is not mistaken for a link that has to resolve."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def check_anchors(problems):
    for path in READMES + DOCS:
        text = read(path)
        defined = set(ANCHOR_TAG.findall(text))
        defined |= {slug(h[1]) for h in HEADING.findall(text)}
        for ref in sorted(set(ANCHOR_REF.findall(strip_code(text))) - defined):
            problems.append(f"{path}: link to #{ref} matches no heading or anchor")


def check_emoji_headings(problems):
    """An emoji in a heading changes the id, so a hand-written link misses it."""
    emoji = re.compile("[\U0001f000-\U0001faff☀-➿]")
    for path in READMES + DOCS:
        for heading in HEADING.findall(read(path)):
            if emoji.search(heading[1]):
                problems.append(f"{path}: heading carries an emoji, which breaks its anchor: {heading[1]!r}")


def check_duplicates(problems):
    for path in READMES:
        counts = collections.Counter(name for name, _ in entry_lines(read(path)))
        for name, n in sorted(counts.items()):
            if n > 1 and name not in ENTRY_EXEMPT:
                problems.append(f"{path}: {name!r} is listed {n} times; a work is listed once")


def check_parity(problems):
    left, right = (entries(read(p)) for p in READMES)
    for name in sorted(set(left) - set(right)):
        problems.append(f"{name!r} is in {READMES[0]} but not {READMES[1]}")
    for name in sorted(set(right) - set(left)):
        problems.append(f"{name!r} is in {READMES[1]} but not {READMES[0]}")
    for name in sorted(set(left) & set(right)):
        if left[name] != right[name]:
            problems.append(f"{name!r} links differ between the two language versions")


def check_files(problems):
    def posix(path):
        return os.path.normpath(path).replace(os.sep, "/")

    for path in READMES + DOCS:
        base = os.path.dirname(os.path.join(ROOT, path))
        for target in FILE_REF.findall(strip_code(read(path))):
            if not os.path.exists(os.path.normpath(os.path.join(base, target))):
                problems.append(f"{path}: links to {target}, which does not exist")
    # The reverse direction: a file nothing links to is unreachable for a reader.
    linked = set()
    for path in READMES + DOCS:
        base = os.path.dirname(path)
        for target in FILE_REF.findall(strip_code(read(path))):
            linked.add(posix(os.path.join(base, target)))
    for folder in ("assets", "docs"):
        for name in sorted(os.listdir(os.path.join(ROOT, folder))):
            rel = posix(os.path.join(folder, name))
            if rel in linked:
                continue
            # Images are referenced as ![alt](path), which FILE_REF also catches.
            if any(rel in read(p) for p in READMES + DOCS + ["index.html"]):
                continue
            problems.append(f"{rel} is in the repository but nothing links to it")


def check_site_data(problems):
    """The project page's explorer is generated from README.md; a stale copy
    would show readers a list that no longer matches the one they can cite."""
    import subprocess

    done = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "build_site_data.py"), "--check"],
        capture_output=True, text=True,
    )
    if done.returncode != 0:
        problems.append((done.stdout + done.stderr).strip())


def check_evidence_and_taxonomy(problems):
    import json
    import subprocess
    from build_site_data import read_entries, read_verdicts

    result = subprocess.run([sys.executable, os.path.join(ROOT, "scripts/build_evidence.py"), "--check"], capture_output=True, text=True)
    if result.returncode:
        problems.append((result.stdout + result.stderr).strip())
    taxonomy = json.loads(read("data/taxonomy.json"))
    expected = {r["name"]: r for r in taxonomy}
    actual, _ = read_entries(read_verdicts())
    actual = {r["name"]: r for r in actual if r["group"] in {"interpreted", "executable", "evaluation"}}
    if expected.keys() != actual.keys():
        problems.append("Taxonomy/README membership differs: " + str(expected.keys() ^ actual.keys()))
    for name in expected.keys() & actual.keys():
        if expected[name]["mechanism"] != actual[name]["node"]:
            problems.append(f"Taxonomy placement differs: {name}")
    evidence = json.loads(read("data/reported-evidence.json"))["methods"]
    methods = {r["key"] for r in taxonomy if not r["branch"].startswith("Evaluation")}
    if methods != {r["key"] for r in evidence}:
        problems.append("Evidence population differs from taxonomy update targets")
    for row in evidence:
        entry = actual.get(row["name"], {})
        if row["url"] not in [url for _, url in entry.get("links", [])]:
            problems.append(f'Evidence source link differs: {row["name"]}')



def check_citation(problems):
    """Keep the manuscript citation identical in both READMEs and the site."""
    import html

    citations = []
    for path in READMES:
        match = re.search(r"```bibtex\n(.*?)\n```", read(path), re.S)
        if not match:
            problems.append(f"{path}: missing BibTeX citation")
            return
        citations.append(match.group(1))
    match = re.search(r'<pre class="bib" id="bib">(.*?)</pre>', read("index.html"), re.S)
    if not match:
        problems.append("index.html: missing BibTeX citation")
        return
    citations.append(html.unescape(re.sub(r"<[^>]+>", "", match.group(1))))
    if len({" ".join(citation.split()) for citation in citations}) != 1:
        problems.append("Manuscript citation differs between READMEs and website")


def check_paper_snapshot(problems):
    """Both public PDFs and bibliographies must match their recorded source snapshots."""
    import hashlib
    import json
    from pathlib import Path

    snapshot = json.loads(read("data/source-snapshot.json"))
    short = snapshot["short_paper"]
    artifacts = {
        snapshot["paper_pdf"]: snapshot["sha256"]["main.pdf"],
        short["paper_pdf"]: short["sha256"]["main.pdf"],
        snapshot["bibliographies"]["full"]: snapshot["sha256"]["references.bib"],
        snapshot["bibliographies"]["short"]: short["sha256"]["references.bib"],
    }
    for relative_path, expected_hash in artifacts.items():
        artifact = Path(ROOT) / relative_path
        if not artifact.is_file():
            problems.append(f"Public manuscript artifact is missing: {relative_path}")
            continue
        data = artifact.read_bytes()
        if artifact.suffix == ".bib":
            # Git for Windows checks text out as CRLF by default; the snapshot records LF bytes.
            data = data.replace(b"\r\n", b"\n")
        if hashlib.sha256(data).hexdigest() != expected_hash:
            problems.append(f"Manuscript artifact differs from its snapshot: {relative_path}")



def check_html(problems):
    from html.parser import HTMLParser
    from urllib.parse import urlsplit, unquote

    class PageParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.ids = set()
            self.refs = []
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if "id" in attrs:
                if attrs["id"] in self.ids:
                    problems.append("index.html: duplicate id " + attrs["id"])
                self.ids.add(attrs["id"])
            for key in ("src", "href"):
                if attrs.get(key):
                    self.refs.append(attrs[key])

    page = PageParser()
    page.feed(read("index.html"))
    for ref in page.refs:
        url = urlsplit(ref)
        if url.scheme or url.netloc:
            continue
        if url.path and not os.path.exists(os.path.join(ROOT, unquote(url.path))):
            problems.append("index.html: missing local file " + url.path)
        if not url.path and url.fragment and url.fragment not in page.ids:
            problems.append("index.html: broken anchor " + url.fragment)
    if "scrollIntoView" in read("site/app.js"):
        problems.append("site/app.js: scrollIntoView disrupts embedded previews")


def check_links(problems):
    import concurrent.futures
    import subprocess

    urls = set()
    for path in READMES + DOCS:
        urls.update(
            u for u in re.findall(r"\]\((https?://[^)]+)\)", strip_code(read(path)))
            if "shields.io" not in u and "awesome.re" not in u
        )

    def status(url):
        done = subprocess.run(
            ["curl", "-sIL", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "25", url],
            capture_output=True, text=True,
        )
        return url, done.stdout.strip()

    with concurrent.futures.ThreadPoolExecutor(10) as pool:
        results = list(pool.map(status, sorted(urls)))
    # 403 is a publisher blocking the request, not a broken link; those DOIs are
    # confirmed through Crossref instead.
    for url, code in sorted(results):
        if code not in ("200", "202", "301", "302", "403"):
            problems.append(f"{url} returned {code or 'no response'}")
    print(f"checked {len(results)} links")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--links", action="store_true", help="also resolve every URL (needs network)")
    args = parser.parse_args()

    problems = []
    check_anchors(problems)
    check_emoji_headings(problems)
    check_duplicates(problems)
    check_parity(problems)
    check_files(problems)
    check_site_data(problems)
    check_evidence_and_taxonomy(problems)
    check_html(problems)
    check_citation(problems)
    check_paper_snapshot(problems)
    if args.links:
        check_links(problems)

    counts = {p: len(entries(read(p))) for p in READMES}
    print("entries: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    with_code = sum(1 for links in entries(read(READMES[0])).values() if len(links) > 1)
    print(f"entries with a second link: {with_code}")

    if problems:
        print(f"\n{len(problems)} problem(s):")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
