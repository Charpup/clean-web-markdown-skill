import unittest
from unittest.mock import patch

import scripts.fetch_markdown as fm


class FetchMarkdownTests(unittest.TestCase):
    def test_normalize_url_adds_scheme(self):
        self.assertEqual(fm.normalize_url("example.com"), "https://example.com")

    def test_markdown_like_detects_heading(self):
        text = "# Title\n\nSome content with [link](https://example.com)"
        self.assertTrue(fm.is_markdown_like(text))

    def test_markdown_like_rejects_short(self):
        self.assertFalse(fm.is_markdown_like("short text"))

    def test_strategy_order_auto(self):
        self.assertEqual(fm.strategy_order("auto"), ["cloudflare", "jina", "firecrawl"])

    def test_strategy_order_single(self):
        self.assertEqual(fm.strategy_order("jina"), ["jina"])

    def test_build_jina_url(self):
        url = "https://example.com/a"
        self.assertEqual(fm.build_jina_url(url), "https://r.jina.ai/https://example.com/a")

    @patch("scripts.fetch_markdown.http_post_json")
    def test_fetch_firecrawl_reads_nested_markdown(self, mock_post):
        markdown = "# 标题\\n\\n- 项目 A：说明更详细一些\\n- 项目 B：[链接](https://example.com)"
        mock_post.return_value = (200, '{"data": {"markdown": "' + markdown + '"}}', {})
        result = fm.fetch_firecrawl("https://example.com", "test-key")
        self.assertEqual(result, "# 标题\n\n- 项目 A：说明更详细一些\n- 项目 B：[链接](https://example.com)")


if __name__ == "__main__":
    unittest.main()
