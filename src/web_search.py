import requests
from typing import List, Dict
from urllib.parse import quote_plus
from bs4 import BeautifulSoup


class WebSearchTool:
    """Ferramenta personalizada para pesquisa web usando DuckDuckGo"""

    def __init__(self) -> None:
        self.name = "web_search"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                )
            }
        )

    def search_web(self, query: str, num_results: int = 5, focus_news: bool = True) -> List[Dict[str, str]]:
        """Pesquisa na web usando DuckDuckGo"""
        try:
            if focus_news:
                news_sites = (
                    "site:g1.globo.com OR site:folha.uol.com.br OR site:estadao.com.br "
                    "OR site:uol.com.br OR site:cnnbrasil.com.br OR site:bbc.com"
                )
                search_query = f"{query} notícias news ({news_sites})"
            else:
                search_query = query

            encoded_query = quote_plus(search_query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

            response = self.session.get(url, timeout=(3.05, 6))
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            results: List[Dict[str, str]] = []
            result_divs = soup.find_all("div", class_="result")

            for div in result_divs[:num_results]:
                try:
                    title_element = div.find("a", class_="result__a")
                    if not title_element:
                        continue

                    title = title_element.get_text(strip=True)
                    raw_link = title_element.get("href", "")
                    link = raw_link
                    try:
                        from urllib.parse import urlparse, parse_qs, unquote

                        if raw_link.startswith("/l/?") or "duckduckgo.com/l/?" in raw_link:
                            raw_link_abs = (
                                f"https://duckduckgo.com{raw_link}" if raw_link.startswith("/l/?") else raw_link
                            )
                            parsed = urlparse(raw_link_abs)
                            qs = parse_qs(parsed.query)
                            uddg = qs.get("uddg", [None])[0]
                            if uddg:
                                link = unquote(uddg)
                    except Exception:
                        pass

                    snippet_element = div.find("a", class_="result__snippet")
                    snippet = (
                        snippet_element.get_text(strip=True)
                        if snippet_element
                        else "Sem resumo disponível"
                    )

                    if title and link:
                        results.append({"titulo": title, "link": link, "resumo": snippet})
                except Exception:
                    continue

            return results if results else self._get_fallback_data(query)
        except Exception:
            return self._get_fallback_data(query)

    def extract_content(self, url: str) -> str:
        """Extrai conteúdo de uma URL específica"""
        try:
            response = self.session.get(url, timeout=(3.05, 6))
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)
            return text[:2000]
        except Exception as e:
            return f"Erro ao extrair conteúdo: {e}"

    def _get_fallback_data(self, tema: str) -> List[Dict[str, str]]:
        """Sem fallback simulado para evitar fontes inexistentes."""
        return []
