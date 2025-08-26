from unittest.mock import Mock, patch

from src.content_agent import ContentGeneratorAgent


def test_generate_structured_content():
    with patch("src.content_agent.OpenAI") as mock_openai, patch("src.image_generation.OpenAI") as mock_img_openai:
        mock_client = Mock()
        completion = Mock()
        completion.choices = [Mock(message=Mock(content='{"titulo": "T", "subtitulo": "S", "conteudo": "C"}'))]
        mock_client.chat.completions.create.return_value = completion
        mock_openai.return_value = mock_client
        mock_img_openai.return_value = Mock()

        agent = ContentGeneratorAgent()
        agent.web_search_tool.search_web = Mock(return_value=[])
        agent.image_generator.generate_image = Mock(return_value=None)
        result = agent.generate_structured_content("tema", generate_image=False)
    assert result["titulo"] == "T"
    assert "fontes" in result
