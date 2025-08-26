from unittest.mock import Mock, patch

from src.workflow import ResearchWorkflow


def test_workflow_run_uses_agent():
    with patch("src.workflow.ContentGeneratorAgent") as mock_agent_cls:
        mock_agent = Mock()
        mock_agent.generate_structured_content.return_value = {
            "titulo": "T",
            "subtitulo": "S",
            "conteudo": "C",
            "fontes": [],
            "imagem": None,
        }
        mock_agent_cls.return_value = mock_agent
        workflow = ResearchWorkflow()
        result = workflow.run("tema", generate_image=False)
    assert result["tema"] == "tema"
    assert result["conteudo"]["titulo"] == "T"
