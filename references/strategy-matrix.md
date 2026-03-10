# Strategy Matrix

## Priority order (auto)

1. **cloudflare** (Accept negotiation)
2. **jina** (r.jina.ai prefix)
3. **firecrawl** (API)

## Selection guidance

- Fastest and cheapest first: cloudflare
- JS-heavy and cluttered page: jina
- Complex dynamic/auth scraping: firecrawl

## Notes

- Cloudflare markdown negotiation depends on site/network path support.
- Jina provides strong article extraction and usually removes nav/ads.
- Firecrawl is best for robust crawling pipelines and structured scraping.
