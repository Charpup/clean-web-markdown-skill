#!/usr/bin/env python3
"""Fetch clean markdown for AI agents with multi-strategy fallback."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from typing import Callable, Dict, List, Optional, Tuple


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        raise ValueError("url is empty")
    if not re.match(r"^https?://", url):
        url = "https://" + url
    return url


def is_markdown_like(text: str) -> bool:
    if not text or len(text.strip()) < 40:
        return False
    signals = [r"^#\s+", r"\n##\s+", r"\n[-*]\s+", r"\[[^\]]+\]\([^\)]+\)"]
    score = sum(1 for p in signals if re.search(p, text, flags=re.MULTILINE))
    return score >= 1


def http_get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 20) -> Tuple[int, str, Dict[str, str]]:
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
        body = resp.read().decode("utf-8", errors="replace")
        meta = {k.lower(): v for k, v in resp.headers.items()}
        return resp.status, body, meta


def http_post_json(url: str, payload: Dict, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Tuple[int, str, Dict[str, str]]:
    data = json.dumps(payload).encode("utf-8")
    hdrs = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(url, data=data, headers=hdrs, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
        body = resp.read().decode("utf-8", errors="replace")
        meta = {k.lower(): v for k, v in resp.headers.items()}
        return resp.status, body, meta


def fetch_cloudflare(url: str) -> Optional[str]:
    status, body, meta = http_get(
        url,
        headers={
            "Accept": "text/markdown, text/plain;q=0.9, text/html;q=0.7",
            "User-Agent": "Mozilla/5.0 (compatible; clean-web-markdown-skill/1.0)",
        },
    )
    ctype = meta.get("content-type", "")
    if status == 200 and ("markdown" in ctype or is_markdown_like(body)):
        return body.strip()
    return None


def build_jina_url(url: str) -> str:
    return "https://r.jina.ai/" + url


def fetch_jina(url: str) -> Optional[str]:
    jina_url = build_jina_url(url)
    status, body, _ = http_get(jina_url, headers={"User-Agent": "clean-web-markdown-skill/1.0"})
    if status == 200 and is_markdown_like(body):
        return body.strip()
    return None


def fetch_firecrawl(url: str, api_key: str) -> Optional[str]:
    status, body, _ = http_post_json(
        "https://api.firecrawl.dev/v1/scrape",
        payload={"url": url, "formats": ["markdown"]},
        headers={"Authorization": f"Bearer {api_key}"},
    )
    if status != 200:
        return None
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return None

    markdown = (
        data.get("data", {}).get("markdown")
        or data.get("markdown")
        or data.get("content")
    )
    if isinstance(markdown, str) and is_markdown_like(markdown):
        return markdown.strip()
    return None


def strategy_order(strategy: str) -> List[str]:
    if strategy == "auto":
        return ["cloudflare", "jina", "firecrawl"]
    return [strategy]


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch clean markdown from web pages")
    parser.add_argument("url", help="target URL")
    parser.add_argument("--strategy", choices=["auto", "cloudflare", "jina", "firecrawl"], default="auto")
    parser.add_argument("--firecrawl-api-key", default="")
    args = parser.parse_args()

    try:
        url = normalize_url(args.url)
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2

    providers: Dict[str, Callable[[], Optional[str]]] = {
        "cloudflare": lambda: fetch_cloudflare(url),
        "jina": lambda: fetch_jina(url),
        "firecrawl": lambda: fetch_firecrawl(url, args.firecrawl_api_key) if args.firecrawl_api_key else None,
    }

    for name in strategy_order(args.strategy):
        markdown = providers[name]()
        if markdown:
            print(json.dumps({"ok": True, "strategy": name, "url": url, "markdown": markdown}, ensure_ascii=False))
            return 0

    print(json.dumps({"ok": False, "url": url, "strategy": args.strategy, "error": "all strategies failed"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    sys.exit(main())
