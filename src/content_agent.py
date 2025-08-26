import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional, List

from openai import OpenAI

from .web_search import WebSearchTool
from .image_generation import ImageGeneratorTool


class ContentGeneratorAgent:
    """Agente especializado em geração de conteúdo estruturado"""

    def __init__(self) -> None:
        self.web_search_tool = WebSearchTool()
        self.image_generator = ImageGeneratorTool()
        self.client = OpenAI()

    def generate_structured_content(
        self,
        tema: str,
        generate_image: bool = True,
        estilo_imagem: str = "realista",
        tamanho: Optional[str] = None,
    ) -> Dict[str, Any]:
        search_results = self.web_search_tool.search_web(tema, num_results=3, focus_news=True)

        def _is_valid_source(item: Dict[str, str]) -> bool:
            link = item.get("link", "")
            title = item.get("titulo", "")
            if not link.startswith("http"):
                return False
            if "exemplo" in link or "example" in link.lower():
                return False
            if not title:
                return False
            return True

        valid_sources = [r for r in search_results if _is_valid_source(r)]

        enriched_snippets: List[str] = []
        to_fetch = valid_sources[:3]

        def fetch_item(it: Dict[str, str]) -> str:
            try:
                page_text = self.web_search_tool.extract_content(it["link"])
                if page_text and not page_text.lower().startswith("erro ao extrair"):
                    return f"- {it['titulo']}: {page_text[:600]}"
                return f"- {it['titulo']}: {it['resumo']}"
            except Exception:
                return f"- {it['titulo']}: {it['resumo']}"

        if to_fetch:
            with ThreadPoolExecutor(max_workers=min(3, len(to_fetch))) as executor:
                future_map = {executor.submit(fetch_item, it): it for it in to_fetch}
                for fut in as_completed(future_map):
                    enriched_snippets.append(fut.result())
        if not enriched_snippets:
            enriched_snippets = [f"- {r['titulo']}: {r['resumo']}" for r in valid_sources]

        snippets_text = "\n".join(enriched_snippets)
        prompt = f"""
        Com base nas seguintes informações pesquisadas sobre "{tema}":

        {snippets_text}

        Crie um texto estruturado em formato JSON com as seguintes chaves:
        - "titulo": Um título atrativo e informativo
        - "subtitulo": Um subtítulo que complemente o título
        - "conteudo": Um texto detalhado e bem estruturado (mínimo 200 palavras)

        O conteúdo deve ser informativo, bem escrito e baseado nas informações fornecidas.
        Retorne APENAS o JSON, sem texto adicional.
        """

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um especialista em criação de conteúdo estruturado. Analise informações de "
                        "múltiplas fontes e crie textos bem organizados. Inclua fontes somente se forem reais e verificáveis; "
                        "não invente fontes. Retorne apenas JSON válido com as chaves: titulo, subtitulo, conteudo. "
                        "Não inclua rótulos textuais (como 'Título:', 'Subtítulo:' ou 'Conteúdo:') dentro dos valores."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        try:
            response_text = response.choices[0].message.content

            def _clean_value(s: str) -> str:
                import re

                s = s.strip()
                pattern = r"^\s*(?:t[íi]tulo|subt[íi]tulo|conte[uú]do)\s*[:：]\s*"
                s = re.sub(pattern, "", s, flags=re.IGNORECASE)
                return s.strip()

            try:
                content_data = json.loads(response_text)
            except Exception:
                import re

                m = re.search(r"\{[\s\S]*\}", response_text)
                if m:
                    content_data = json.loads(m.group(0))
                else:
                    raise

            required_keys = ["titulo", "subtitulo", "conteudo"]
            if all(key in content_data for key in required_keys):
                content_data["titulo"] = _clean_value(str(content_data.get("titulo", "")))
                content_data["subtitulo"] = _clean_value(str(content_data.get("subtitulo", "")))
                content_data["conteudo"] = _clean_value(str(content_data.get("conteudo", "")))
                image_data = None
                if generate_image:
                    image_data = self.image_generator.generate_image(
                        titulo=content_data["titulo"],
                        elementos=[tema],
                        estilo_imagem=estilo_imagem,
                        size=tamanho,
                    )

                content_data["fontes"] = [
                    {
                        "titulo": result["titulo"],
                        "link": result["link"],
                        "resumo": result["resumo"],
                    }
                    for result in valid_sources
                ]

                if image_data and isinstance(image_data, dict) and "error" in image_data:
                    content_data["imagem"] = None
                    content_data["imagem_error"] = image_data["error"]
                elif image_data:
                    content_data["imagem"] = image_data
                else:
                    content_data["imagem"] = None

                return content_data
            else:
                raise ValueError("Estrutura JSON inválida")
        except (json.JSONDecodeError, ValueError):
            raw_text = response.content if hasattr(response, "content") else str(response)

            def _strip_labels(txt: str) -> str:
                import re

                txt = txt.strip()
                pattern = r"^\s*(?:t[íi]tulo|subt[íi]tulo|conte[uú]do)\s*[:：]\s*"
                txt = re.sub(pattern, "", txt, flags=re.IGNORECASE)
                return txt.strip()

            raw_text = _strip_labels(raw_text)
            return {
                "titulo": "",
                "subtitulo": "",
                "conteudo": raw_text,
                "fontes": valid_sources,
                "imagem": None,
            }
