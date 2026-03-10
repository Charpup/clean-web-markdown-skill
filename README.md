# clean-web-markdown-skill

> Markdown-first web retrieval skill for AI agents (Cloudflare negotiation → Jina → Firecrawl fallback)

## ✨ Why

Agents often waste tokens on noisy HTML. This skill prioritizes clean markdown responses so downstream summarization/RAG is cheaper and more reliable.

## 🧠 Strategy Chain

1. **Cloudflare Markdown Negotiation** (`Accept: text/markdown`)
2. **Jina Reader** (`https://r.jina.ai/<url>`)
3. **Firecrawl** (`/v1/scrape`, markdown format)

## 🚀 Quick Start

```bash
python3 scripts/fetch_markdown.py "https://example.com/blog/post"
```

### 中文使用示例

```bash
# 抓网页正文并输出干净 Markdown
python3 scripts/fetch_markdown.py "https://example.com/文章"

# 强制走 Jina
python3 scripts/fetch_markdown.py "https://example.com" --strategy jina
```

Force provider:

```bash
python3 scripts/fetch_markdown.py "https://example.com" --strategy jina
python3 scripts/fetch_markdown.py "https://example.com" --strategy firecrawl --firecrawl-api-key "$FIRECRAWL_API_KEY"
```

## 📦 Output

```json
{
  "ok": true,
  "strategy": "jina",
  "url": "https://example.com",
  "markdown": "# Title ..."
}
```

## 🎯 Trigger Phrases (EN + 中文)

Use this skill when user requests look like:

- fetch/read/summarize this page as markdown
- clean this URL before summarizing
- 抓网页正文
- 提取网页 Markdown
- 网页转 Markdown
- 读取网页并总结
- 这个链接帮我清洗一下

## 🧪 Tests

```bash
python3 -m unittest tests/test_fetch_markdown.py
```

## 🧩 OpenClaw Skill

- Skill entry: `SKILL.md`
- Script: `scripts/fetch_markdown.py`
- Strategy reference: `references/strategy-matrix.md`

## 📄 License

MIT
