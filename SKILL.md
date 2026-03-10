---
name: clean-web-markdown
description: Retrieve clean markdown from webpages for AI agents using protocol-level content negotiation and crawl-to-markdown fallbacks. Use when users ask to fetch/read/summarize websites with low-noise markdown, to improve web_fetch quality, or to process JS-heavy pages via Jina/Firecrawl. Chinese trigger cues include: "抓网页正文", "提取网页 Markdown", "网页转 Markdown", "读取网页并总结", "这个链接帮我清洗一下".
---

# clean-web-markdown

Use this skill to get low-noise markdown from web pages with a deterministic fallback chain.

## Usage cues (EN + 中文)

Trigger this skill when requests match patterns like:

- "fetch this page as clean markdown"
- "summarize this URL, skip noisy HTML"
- "抓网页正文"
- "提取网页 Markdown"
- "网页转 Markdown"
- "读取网页并总结"
- "这个链接帮我清洗一下"

## Workflow

1. Normalize input URL.
2. Try **Cloudflare-style markdown negotiation** first:
   - send `Accept: text/markdown`
   - keep normal browser-like user-agent
3. If response is not usable markdown, fallback to **Jina Reader**:
   - request `https://r.jina.ai/<url>`
4. If user provides Firecrawl API key and page is still problematic, try **Firecrawl scrape API**.
5. Return markdown + source strategy used.

## Use in agent web access flow

When agent needs website content:

- Prefer this skill before raw HTML extraction.
- Keep `web_fetch` as fallback when markdown service fails.
- For JS-heavy pages or paywall-like structure:
  - try Jina first
  - then Firecrawl (if key available)

## Commands

### Direct script

```bash
python3 scripts/fetch_markdown.py "https://example.com/article"
```

### Force strategy

```bash
python3 scripts/fetch_markdown.py "https://example.com/article" --strategy cloudflare
python3 scripts/fetch_markdown.py "https://example.com/article" --strategy jina
python3 scripts/fetch_markdown.py "https://example.com/article" --strategy firecrawl --firecrawl-api-key "$FIRECRAWL_API_KEY"
```

## Output contract

Script returns JSON:

- `ok`: boolean
- `strategy`: selected provider
- `url`: original url
- `markdown`: cleaned markdown text
- `error`: present when failed

## References

- Strategy details and decision matrix: `references/strategy-matrix.md`
