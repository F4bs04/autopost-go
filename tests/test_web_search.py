from unittest.mock import patch

from src.web_search import WebSearchTool


def test_search_web_returns_empty_on_error():
    tool = WebSearchTool()
    with patch.object(tool.session, "get", side_effect=Exception("network")):
        results = tool.search_web("python", num_results=1)
    assert results == []
