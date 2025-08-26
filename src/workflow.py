import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from .content_agent import ContentGeneratorAgent


class ResearchWorkflow:
    """Workflow principal para pesquisa e geração de conteúdo"""

    def __init__(self) -> None:
        self.name = "ResearchWorkflow"
        self.description = (
            "Workflow para pesquisa web e geração de conteúdo estruturado"
        )
        self.content_agent = ContentGeneratorAgent()

    def run(
        self,
        tema: str,
        generate_image: bool = True,
        estilo_imagem: str = "realista",
        tamanho: Optional[str] = None,
    ) -> Dict[str, Any]:
        print(f"Iniciando pesquisa sobre: {tema}")
        content_data = self.content_agent.generate_structured_content(
            tema,
            generate_image=generate_image,
            estilo_imagem=estilo_imagem,
            tamanho=tamanho,
        )
        result = {
            "tema": tema,
            "data_geracao": datetime.now().isoformat(),
            "conteudo": content_data,
            "workflow_version": "agno-1.0",
        }
        print("Conteudo gerado com sucesso!")
        return result

    def save_results(self, data: Dict[str, Any], output_dir: str = "output") -> None:
        os.makedirs(output_dir, exist_ok=True)
        tema_filename = data["tema"].replace(" ", "_").replace("/", "_")
        json_path = os.path.join(output_dir, f"{tema_filename}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        md_content = self._convert_to_markdown(data)
        md_path = os.path.join(output_dir, f"{tema_filename}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print("Arquivos salvos:")
        print(f"   JSON: {json_path}")
        print(f"   Markdown: {md_path}")

    def _convert_to_markdown(self, data: Dict[str, Any]) -> str:
        content = data["conteudo"]
        md = f"# {content['titulo']}\n\n"
        md += f"## {content['subtitulo']}\n\n"
        if "imagem" in content and content["imagem"]:
            image_info = content["imagem"]
            md += (
                f"![Imagem sobre {content['titulo']}]({image_info['local_path']})\n\n"
            )
            md += (
                f"*Imagem gerada automaticamente usando {image_info['modelo']}*\n\n"
            )
        md += f"{content['conteudo']}\n\n"
        if "fontes" in content and content["fontes"]:
            md += "## Fontes Consultadas\n\n"
            for i, fonte in enumerate(content["fontes"], 1):
                md += f"{i}. **{fonte['titulo']}**\n"
                md += f"   - Link: {fonte['link']}\n"
                md += f"   - Resumo: {fonte['resumo']}\n\n"
        md += "---\n\n"
        md += f"**Tema:** {data['tema']}\n\n"
        md += f"**Data de Geração:** {data['data_geracao']}\n\n"
        md += f"**Versão:** {data.get('workflow_version', 'N/A')}\n\n"
        md += "*Gerado automaticamente pelo Agente de IA com Agno Framework*\n"
        return md


def main() -> None:
    """Função principal para executar o workflow"""
    tema = "canabis medicinal"
    try:
        workflow = ResearchWorkflow()
        resultado = workflow.run(tema)
        workflow.save_results(resultado)
        print("\nProcesso concluido com sucesso!")
        print(f"Tema processado: {tema}")
        print(f"Titulo gerado: {resultado['conteudo']['titulo']}")
        print(f"Fontes encontradas: {len(resultado['conteudo']['fontes'])}")
    except Exception as e:
        print(f"Erro durante execucao: {e}")
        raise


if __name__ == "__main__":
    main()
