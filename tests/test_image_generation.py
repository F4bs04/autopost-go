from unittest.mock import Mock, patch

from src.image_generation import ImageGeneratorTool


def test_create_image_prompt_contains_title_and_elements():
    with patch("src.image_generation.OpenAI") as mock_openai:
        mock_openai.return_value = Mock()
        tool = ImageGeneratorTool()
    prompt = tool._create_image_prompt("Titulo", ["elemento"])
    assert "Titulo" in prompt
    assert "elemento" in prompt
