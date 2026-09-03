"""Conservative listing-page crawler for sources with RSS, JSON-LD, or dated HTML cards."""
import email.utils
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

CONFIG = json.loads((Path(__file__).with_name("generic_sources.json")).read_text(encoding="utf-8"))
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HotEduNews/1.0; +https://github.com/xutao-91/hot-edu-news)"}
DATE_RE = re.compile(r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s+\d{1,2},?\s+\d{4}\b|\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b")

def parse_date(value):
    if not value:
        return None
    value = str(value).strip()
    for candidate in (value, value[:10]):
        try:
            return datetime.fromisoformat(candidate.replace("Z", "+00:00")).date()
        except ValueError:
            pass
    try:
        return email.utils.parsedate_to_datetime(value).date()
    except (TypeError, ValueError, IndexError):
        pass
    normalized = value.replace(".", "")
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(normalized, fmt).date()
        except ValueError:
            pass
    match = DATE_RE.search(value)
    return parse_date(match.group(0)) if match else None

def within(date, cutoff):
    return date is not None and date >= cutoff

def text(node):
    return node.get_text(" ", strip=True) if node else ""

def add_article(items, seen, title, url, date, summary=""):
    if not title or not url or url in seen or not date:
        return
    seen.add(url)
    items.append({"title": title[:500], "url": url, "date": date.isoformat(), "summary_en": summary[:500]})

def iter_json(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_json(child)

def extract_jsonld(soup, base_url, cutoff):
    items, seen = [], set()
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(script.string or script.get_text())
        except (json.JSONDecodeError, TypeError):
            continue
        for node in iter_json(payload):
            types = node.get("@type", [])
            types = [types] if isinstance(types, str) else types
            if not any("article" in str(kind).lower() or "report" in str(kind).lower() for kind in types):
                continue
            url = node.get("url") or node.get("mainEntityOfPage")
            if isinstance(url, dict):
                url = url.get("@id")
            add_article(items, seen, node.get("headline") or node.get("name"), urljoin(base_url, url or ""), parse_date(node.get("datePublished") or node.get("dateModified")), node.get("description") or "")
    return [item for item in items if within(parse_date(item["date"]), cutoff)]

def extract_html(soup, base_url, cutoff):
    items, seen = [], set()
    blocks = soup.select("article") or soup.select("li, div")
    for block in blocks:
        heading = block.select_one("h1 a[href], h2 a[href], h3 a[href], h4 a[href]")
        if not heading:
            continue
        url = urljoin(base_url, heading.get("href", ""))
        if urlparse(url).netloc != urlparse(base_url).netloc:
            continue
        date_node = block.select_one("time[datetime], time, .date, .published, .post-date")
        date = parse_date(date_node.get("datetime") if date_node and date_node.has_attr("datetime") else text(date_node))
        if not date:
            date = parse_date(text(block))
        summary = text(block.select_one("p, .summary, .excerpt, .description"))
        if within(date, cutoff):
            add_article(items, seen, text(heading), url, date, summary)
    return items

def run(source_key, days=4):
    spec = CONFIG[source_key]
    cutoff = datetime.now(timezone.utc).date() - timedelta(days=days)
    response = requests.get(spec["source_url"], headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    articles = extract_jsonld(soup, spec["source_url"], cutoff)
    if not articles:
        articles = extract_html(soup, spec["source_url"], cutoff)
    for article in articles:
        article.update({"source": spec["source"], "category": spec["category"]})
    output_dir = Path("data/raw") / source_key
    output_dir.mkdir(parents=True, exist_ok=True)
    output = {"source": spec["source"], "source_url": spec["source_url"], "crawled_at": datetime.now().isoformat(), "total_news": len(articles), "news": articles}
    (output_dir / f"{datetime.now():%Y-%m-%d}.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] {spec['source']}: {len(articles)} 篇文章")
    return output
