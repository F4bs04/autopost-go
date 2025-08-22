"""
Agente de IA com Agno Framework
Versão experimental que usa Agno como base principal do projeto.
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from PIL import Image
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class WebSearchTool:
    """Ferramenta personalizada para pesquisa web usando DuckDuckGo"""
    
    def __init__(self):
        self.name = "web_search"
        # Reutilizar conexões HTTP para reduzir latência de conexão/TLS
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_web(self, query: str, num_results: int = 5, focus_news: bool = True) -> List[Dict[str, str]]:
        """
        Pesquisa na web usando DuckDuckGo
        
        Args:
            query: Termo de pesquisa
            num_results: Número de resultados desejados
            focus_news: Se deve focar em sites de notícias
            
        Returns:
            Lista de dicionários com título, link e resumo
        """
        try:
            # Modificar query para focar em notícias se solicitado
            if focus_news:
                news_sites = "site:g1.globo.com OR site:folha.uol.com.br OR site:estadao.com.br OR site:uol.com.br OR site:cnnbrasil.com.br OR site:bbc.com"
                search_query = f"{query} notícias news ({news_sites})"
            else:
                search_query = query
            
            # Codificar a query para URL
            encoded_query = quote_plus(search_query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            # Usar Session para reuso de conexão
            response = self.session.get(url, timeout=(3.05, 6))
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Extrair resultados da pesquisa
            result_divs = soup.find_all('div', class_='result')
            
            for div in result_divs[:num_results]:
                try:
                    # Extrair título e link
                    title_element = div.find('a', class_='result__a')
                    if not title_element:
                        continue
                    
                    title = title_element.get_text(strip=True)
                    raw_link = title_element.get('href', '')
                    link = raw_link
                    # Em resultados HTML do DuckDuckGo, links podem vir como redirects /l/?uddg=...
                    try:
                        from urllib.parse import urlparse, parse_qs, unquote
                        if raw_link.startswith('/l/?') or 'duckduckgo.com/l/?' in raw_link:
                            # Montar URL absoluta se necessário
                            if raw_link.startswith('/l/?'):
                                raw_link_abs = f"https://duckduckgo.com{raw_link}"
                            else:
                                raw_link_abs = raw_link
                            parsed = urlparse(raw_link_abs)
                            qs = parse_qs(parsed.query)
                            uddg = qs.get('uddg', [None])[0]
                            if uddg:
                                link = unquote(uddg)
                    except Exception:
                        pass
                    
                    # Extrair resumo
                    snippet_element = div.find('a', class_='result__snippet')
                    snippet = snippet_element.get_text(strip=True) if snippet_element else "Sem resumo disponível"
                    
                    if title and link:
                        results.append({
                            'titulo': title,
                            'link': link,
                            'resumo': snippet
                        })
                
                except Exception as e:
                    print(f"Erro ao processar resultado individual: {e}")
                    continue
            
            return results if results else self._get_fallback_data(query)
            
        except Exception as e:
            print(f"Erro na pesquisa web: {e}")
            return self._get_fallback_data(query)
    
    def extract_content(self, url: str) -> str:
        """
        Extrai conteúdo de uma URL específica
        
        Args:
            url: URL para extrair conteúdo
            
        Returns:
            Conteúdo extraído da página
        """
        try:
            # Reutilizar sessão com cabeçalhos e timeouts ajustados
            response = self.session.get(url, timeout=(3.05, 6))
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remover scripts e estilos
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extrair texto principal
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:2000]  # Limitar tamanho
            
        except Exception as e:
            return f"Erro ao extrair conteúdo: {e}"
    
    def _get_fallback_data(self, tema: str) -> List[Dict[str, str]]:
        """Sem fallback simulado para evitar fontes inexistentes."""
        return []

class ImageGeneratorTool:
    """Ferramenta para geração de imagens usando o endpoint de imagens da OpenAI"""
    
    def __init__(self):
        self.name = "image_generator"
        # Cliente OpenAI (lê OPENAI_API_KEY do ambiente)
        self.client = OpenAI()
        # Permitir configurar o modelo via variável de ambiente
        # Preferência: gpt-image-1; fallback automático para dall-e-3 se necessário
        self.image_model = os.getenv('IMAGE_MODEL', 'gpt-image-1')
        # Tamanho padrão otimizado para compatibilidade e velocidade
        # Para gpt-image-1, suportado: '1024x1024', '1024x1536', '1536x1024', 'auto'
        # Para dall-e-3, tamanhos maiores são permitidos, mas podem ser mais lentos
        self.image_size = os.getenv('IMAGE_SIZE', '1536x1024')
    
    def generate_image(self, titulo: str, elementos: List[str] = None, estilo_imagem: str = "realista", save_to_temp: bool = True) -> Optional[Dict[str, Any]]:
        """
        Gera uma imagem baseada no título e elementos do conteúdo
        
        Args:
            titulo: Título do conteúdo para gerar a imagem
            elementos: Lista de elementos/tópicos principais (opcional)
            estilo_imagem: Estilo da imagem (realista, ilustracao, abstrato, criativo)
            
        Returns:
            Dicionário com informações da imagem gerada ou None se falhar
        """
        try:
            # Criar prompt personalizado baseado no template fornecido
            prompt = self._create_image_prompt(titulo, elementos, estilo_imagem)
            
            print(f"Gerando imagem com prompt: {prompt[:100]}...")
            
            # Gerar imagem usando o modelo de imagens da OpenAI (sem response_format)
            model_to_use = self.image_model
            # Normalizar tamanho conforme o modelo para evitar 400 + retry
            allowed_gpt_image1 = {"1024x1024", "1024x1536", "1536x1024", "auto"}
            size_to_use = self.image_size
            if model_to_use == 'gpt-image-1' and size_to_use not in allowed_gpt_image1:
                size_to_use = '1536x1024'
            try:
                # Preferir base64 no gpt-image-1 para evitar dependência de URL externa
                extra_args = {}
                if model_to_use == 'gpt-image-1':
                    extra_args["response_format"] = "b64_json"
                response = self.client.images.generate(
                    model=model_to_use,
                    prompt=prompt,
                    size=size_to_use,
                    n=1,
                    **extra_args
                )
            except Exception as e:
                # Tentar fallback amplo para dall-e-3 se gpt-image-1 falhar por qualquer motivo
                err_msg = str(e)
                print(f"Erro com {model_to_use}: {err_msg}")
                if model_to_use == 'gpt-image-1':
                    print("Tentando fallback para dall-e-3...")
                    # Ajustar tamanho permitido para dall-e-3
                    allowed_dalle3 = {"1024x1024", "1024x1792", "1792x1024"}
                    size_for_dalle3 = self.image_size if self.image_size in allowed_dalle3 else "1792x1024"
                    # Para dall-e-3, manter padrão (normalmente retorna URL)
                    response = self.client.images.generate(
                        model='dall-e-3',
                        prompt=prompt,
                        size=size_for_dalle3,
                        n=1
                    )
                    model_to_use = 'dall-e-3'
                else:
                    raise

            # Tentar extrair base64; se não houver, usar URL
            data0 = response.data[0]
            image_path = None
            image_url = None
            # Definir diretório de saída (temporário por padrão)
            output_dir = "output/tmp" if save_to_temp else "output"
            if hasattr(data0, 'b64_json') and data0.b64_json:
                image_path = self._save_b64_image(data0.b64_json, titulo, output_dir=output_dir)
            elif hasattr(data0, 'url') and data0.url:
                image_url = data0.url
                image_path = self._download_and_save_image(image_url, titulo, output_dir=output_dir)
            else:
                raise ValueError("Resposta da API de imagens sem b64_json ou url")

            # Construir URL pública com base no diretório
            import os as _os
            _filename = _os.path.basename(image_path) if image_path else None
            public_url = None
            if _filename:
                public_url = f"/temp/{_filename}" if save_to_temp else f"/output/{_filename}"

            result = {
                'url': image_url,
                'local_path': image_path,
                'public_url': public_url,
                'prompt_usado': prompt,
                'modelo': model_to_use,
                'tamanho': self.image_size,
                'data_geracao': datetime.now().isoformat()
            }
            print(f"Imagem gerada e salva: {result}")
            return result
            
        except Exception as e:
            # Propagar mensagem de erro para a camada superior
            err = str(e)
            print(f"Erro ao gerar imagem: {err}")
            return {"error": err}
    
    def _create_image_prompt(self, titulo: str, elementos: List[str] = None, estilo_imagem: str = "realista") -> str:
        """
        Cria o prompt para geração de imagem baseado no template fornecido
        
        Args:
            titulo: Título do conteúdo
            elementos: Lista de elementos principais (opcional)
            estilo_imagem: Estilo da imagem (realista, ilustracao, abstrato, criativo)
            
        Returns:
            Prompt formatado para DALL-E
        """
        # Mapear estilos para palavras-chave específicas
        estilos_keywords = {
            "realista": "fotorrealista, alta qualidade, bem iluminado, composição profissional, detalhado, natural",
            "ilustracao": "ilustração digital, arte conceitual, estilo cartoon, colorido, limpo, vetorial",
            "abstrato": "arte abstrata, formas geométricas, cores vibrantes, minimalista, conceitual, moderno",
            "criativo": "arte criativa, imaginativo, surreal, único, experimental, artístico, inovador"
        }
        
        # Template base adaptado para incluir estilo
        base_prompt = f"Gere uma imagem sobre esse tema #{titulo} que represente esses elementos de forma informativa, seja cuidadoso com os detalhes e evite aberrações, faça com que a imagem seja interessante e humanizada."
        
        # Adicionar elementos específicos se fornecidos
        if elementos and len(elementos) > 0:
            elementos_text = ", ".join(elementos[:5])  # Limitar a 5 elementos
            base_prompt += f" Elementos importantes a incluir: {elementos_text}."
        
        # Adicionar diretrizes de estilo baseadas na seleção
        style_keywords = estilos_keywords.get(estilo_imagem, estilos_keywords["realista"])
        technical_guidelines = f" Estilo: {style_keywords}."
        
        return base_prompt + technical_guidelines
    
    def _download_and_save_image(self, image_url: str, titulo: str, output_dir: str = "output") -> str:
        """
        Baixa e salva a imagem gerada localmente
        
        Args:
            image_url: URL da imagem gerada
            titulo: Título para nomear o arquivo
            output_dir: Diretório de saída
            
        Returns:
            Caminho local da imagem salva
        """
        try:
            # Criar diretório se não existir
            os.makedirs(output_dir, exist_ok=True)
            
            # Nome do arquivo baseado no título (remover caracteres especiais)
            import re
            # Remover caracteres especiais e acentos
            filename = re.sub(r'[^\w\s-]', '', titulo)
            filename = filename.replace(' ', '_').replace('-', '_')
            # Limitar tamanho do nome do arquivo
            filename = filename[:50] if len(filename) > 50 else filename
            filename = f"{filename}_image.jpg"
            filepath = os.path.join(output_dir, filename)
            
            # Baixar a imagem
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Verificar se o conteúdo foi baixado corretamente
            if len(response.content) == 0:
                raise Exception("Conteúdo da imagem vazio")
            
            print(f"Tamanho do conteúdo baixado: {len(response.content)} bytes")
            
            # Converter para JPEG usando Pillow
            from io import BytesIO
            
            # Abrir a imagem baixada
            image = Image.open(BytesIO(response.content))
            print(f"Imagem aberta: {image.size}, modo: {image.mode}")
            
            # Converter para RGB se necessário (JPEG não suporta transparência)
            if image.mode in ('RGBA', 'LA', 'P'):
                print("Convertendo imagem para RGB...")
                # Criar fundo branco
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image)
                image = background
            elif image.mode != 'RGB':
                print(f"Convertendo de {image.mode} para RGB...")
                image = image.convert('RGB')
            
            # Salvar como JPEG com qualidade alta
            print(f"Salvando imagem em: {filepath}")
            image.save(filepath, 'JPEG', quality=95, optimize=True)
            
            # Verificar se o arquivo foi salvo corretamente
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"Arquivo salvo com {file_size} bytes")
                if file_size == 0:
                    raise Exception("Arquivo salvo com 0 bytes")
            return filepath
        except Exception as e:
            print(f"Erro ao salvar imagem (base64): {e}")
            raise

    def _save_b64_image(self, b64_data: str, titulo: str, output_dir: str = "output") -> str:
        """Salva imagem a partir de base64 JSON retornado pela API.
        Retorna o caminho local do arquivo salvo.
        """
        try:
            import re
            import base64
            from io import BytesIO
            os.makedirs(output_dir, exist_ok=True)
            # Sanitizar nome do arquivo
            filename = re.sub(r'[^\w\s-]', '', titulo)
            filename = filename.replace(' ', '_').replace('-', '_')
            filename = filename[:50] if len(filename) > 50 else filename
            filename = f"{filename}_image.jpg"
            filepath = os.path.join(output_dir, filename)

            # Decodificar base64
            img_bytes = base64.b64decode(b64_data)
            image = Image.open(BytesIO(img_bytes))
            # Converter para RGB se necessário
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')

            image.save(filepath, 'JPEG', quality=95, optimize=True)
            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                raise Exception('Falha ao salvar a imagem em disco')
            return filepath
        except Exception as e:
            print(f"Erro ao salvar imagem (b64): {e}")
            raise

class ContentGeneratorAgent:
    """Agente especializado em geração de conteúdo estruturado"""
    
    def __init__(self):
        self.web_search_tool = WebSearchTool()
        self.image_generator = ImageGeneratorTool()
        self.client = OpenAI()
    
    def generate_structured_content(self, tema: str, generate_image: bool = True, estilo_imagem: str = "realista") -> Dict[str, Any]:
        """
        Gera conteúdo estruturado sobre um tema específico
        
        Args:
            tema: Tema para pesquisar e gerar conteúdo
            generate_image: Se deve gerar imagem
            estilo_imagem: Estilo da imagem (realista, ilustracao, abstrato, criativo)
            
        Returns:
            Dicionário com conteúdo estruturado
        """
        # Pesquisar informações sobre o tema
        # Diminuir número de resultados para reduzir parsing e latência
        search_results = self.web_search_tool.search_web(tema, num_results=3, focus_news=True)
        # Validar fontes (evitar exemplos e links inválidos)
        def _is_valid_source(item: Dict[str, str]) -> bool:
            link = item.get('link', '')
            title = item.get('titulo', '')
            if not link.startswith('http'):
                return False
            if 'exemplo' in link or 'example' in link.lower():
                return False
            if not title:
                return False
            return True
        valid_sources = [r for r in search_results if _is_valid_source(r)]
        
        # Preparar contexto com conteúdo real das páginas
        enriched_snippets = []
        # Buscar conteúdos em paralelo para reduzir tempo total (limitado a 3)
        to_fetch = valid_sources[:3]
        def fetch_item(it: Dict[str, str]) -> str:
            try:
                page_text = self.web_search_tool.extract_content(it['link'])
                if page_text and not page_text.lower().startswith('erro ao extrair'):
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
        
        # Prompt para geração de conteúdo estruturado
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
        
        # Gerar resposta usando OpenAI diretamente
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um especialista em criação de conteúdo estruturado. Analise informações de múltiplas fontes e crie textos bem organizados. Inclua fontes somente se forem reais e verificáveis; não invente fontes. Retorne apenas JSON válido com as chaves: titulo, subtitulo, conteudo. Não inclua rótulos textuais (como 'Título:', 'Subtítulo:' ou 'Conteúdo:') dentro dos valores."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        try:
            # Tentar parsear como JSON
            # Extrair conteúdo da resposta do OpenAI
            response_text = response.choices[0].message.content
            def _clean_value(s: str) -> str:
                import re
                s = s.strip()
                # remover rótulos no início (case-insensitive)
                pattern = r'^\s*(?:t[íi]tulo|subt[íi]tulo|conte[uú]do)\s*[:：]\s*'
                s = re.sub(pattern, '', s, flags=re.IGNORECASE)
                return s.strip()

            # 1) tentar parse direto
            try:
                content_data = json.loads(response_text)
            except Exception:
                # 2) tentar extrair o primeiro bloco JSON válido
                import re
                m = re.search(r'\{[\s\S]*\}', response_text)
                if m:
                    content_data = json.loads(m.group(0))
                else:
                    raise
            
            # Validar estrutura
            required_keys = ['titulo', 'subtitulo', 'conteudo']
            if all(key in content_data for key in required_keys):
                # Sanitizar valores (remover rótulos se houver)
                content_data['titulo'] = _clean_value(str(content_data.get('titulo', '')))
                content_data['subtitulo'] = _clean_value(str(content_data.get('subtitulo', '')))
                content_data['conteudo'] = _clean_value(str(content_data.get('conteudo', '')))
                image_data = None
                if generate_image:
                    # Gerar imagem baseada no título
                    print("\nGerando imagem para o conteúdo...")
                    image_data = self.image_generator.generate_image(
                        titulo=content_data['titulo'],
                        elementos=[tema],
                        estilo_imagem=estilo_imagem
                    )
                
                # Adicionar metadados
                content_data['fontes'] = [
                    {
                        'titulo': result['titulo'],
                        'link': result['link'],
                        'resumo': result['resumo']
                    }
                    for result in valid_sources
                ]
                
                # Adicionar informações da imagem se gerada com sucesso
                if image_data and isinstance(image_data, dict) and 'error' in image_data:
                    # Erro explícito vindo da ferramenta
                    print("Não foi possível gerar a imagem")
                    content_data['imagem'] = None
                    content_data['imagem_error'] = image_data['error']
                elif image_data:
                    content_data['imagem'] = image_data
                    print(f"Imagem gerada com sucesso: {image_data['local_path']}")
                else:
                    print("Não foi possível gerar a imagem")
                    content_data['imagem'] = None
                
                return content_data
            else:
                raise ValueError("Estrutura JSON inválida")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Erro ao processar resposta do LLM: {e}")
            # Sem inventar conteúdo estruturado: não criar títulos/subtítulos mockados
            # Retornar conteúdo bruto limpo e apenas fontes validadas
            # Isso evita citar fontes falsas e evita rótulos no texto
            raw_text = response.content if hasattr(response, 'content') else str(response)
            # Sanitizar possíveis rótulos no início
            def _strip_labels(txt: str) -> str:
                import re
                txt = txt.strip()
                pattern = r'^\s*(?:t[íi]tulo|subt[íi]tulo|conte[uú]do)\s*[:：]\s*'
                txt = re.sub(pattern, '', txt, flags=re.IGNORECASE)
                return txt.strip()
            raw_text = _strip_labels(raw_text)
            return {
                'titulo': '',
                'subtitulo': '',
                'conteudo': raw_text,
                'fontes': valid_sources,
                'imagem': None
            }

class ResearchWorkflow:
    """Workflow principal para pesquisa e geração de conteúdo"""
    
    def __init__(self):
        self.name = "ResearchWorkflow"
        self.description = "Workflow para pesquisa web e geração de conteúdo estruturado"
        
        # Inicializar agente
        self.content_agent = ContentGeneratorAgent()
    
    def run(self, tema: str, generate_image: bool = True, estilo_imagem: str = "realista") -> Dict[str, Any]:
        """
        Executa o workflow completo
        
        Args:
            tema: Tema para pesquisar e gerar conteúdo
            generate_image: Se deve gerar imagem
            estilo_imagem: Estilo da imagem (realista, ilustracao, abstrato, criativo)
            
        Returns:
            Resultado completo com metadados
        """
        print(f"Iniciando pesquisa sobre: {tema}")
        
        # Gerar conteúdo estruturado
        content_data = self.content_agent.generate_structured_content(tema, generate_image=generate_image, estilo_imagem=estilo_imagem)
        
        # Adicionar metadados do workflow
        result = {
            'tema': tema,
            'data_geracao': datetime.now().isoformat(),
            'conteudo': content_data,
            'workflow_version': 'agno-1.0'
        }
        
        print("Conteudo gerado com sucesso!")
        return result
    
    def save_results(self, data: Dict[str, Any], output_dir: str = "output"):
        """
        Salva os resultados em JSON e Markdown
        
        Args:
            data: Dados para salvar
            output_dir: Diretório de saída
        """
        # Criar diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Nome do arquivo baseado no tema
        tema_filename = data['tema'].replace(' ', '_').replace('/', '_')
        
        # Salvar JSON
        json_path = os.path.join(output_dir, f"{tema_filename}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Converter para Markdown
        md_content = self._convert_to_markdown(data)
        md_path = os.path.join(output_dir, f"{tema_filename}.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"Arquivos salvos:")
        print(f"   JSON: {json_path}")
        print(f"   Markdown: {md_path}")
    
    def _convert_to_markdown(self, data: Dict[str, Any]) -> str:
        """Converte dados para formato Markdown"""
        content = data['conteudo']
        
        md = f"# {content['titulo']}\n\n"
        md += f"## {content['subtitulo']}\n\n"
        
        # Adicionar imagem se disponível
        if 'imagem' in content and content['imagem']:
            image_info = content['imagem']
            md += f"![Imagem sobre {content['titulo']}]({image_info['local_path']})\n\n"
            md += f"*Imagem gerada automaticamente usando {image_info['modelo']}*\n\n"
        
        md += f"{content['conteudo']}\n\n"
        
        # Adicionar fontes
        if 'fontes' in content and content['fontes']:
            md += "## Fontes Consultadas\n\n"
            for i, fonte in enumerate(content['fontes'], 1):
                md += f"{i}. **{fonte['titulo']}**\n"
                md += f"   - Link: {fonte['link']}\n"
                md += f"   - Resumo: {fonte['resumo']}\n\n"
        
        # Adicionar metadados
        md += "---\n\n"
        md += f"**Tema:** {data['tema']}\n\n"
        md += f"**Data de Geração:** {data['data_geracao']}\n\n"
        md += f"**Versão:** {data.get('workflow_version', 'N/A')}\n\n"
        md += "*Gerado automaticamente pelo Agente de IA com Agno Framework*\n"
        
        return md

def main():
    """Função principal para executar o workflow"""
    # Tema definido no código (pode ser alterado aqui)
    tema = "canabis medicinal"  # ← MUDE AQUI para outro tema
    
    try:
        # Inicializar workflow
        workflow = ResearchWorkflow()
        
        # Executar pesquisa e geração
        resultado = workflow.run(tema)
        
        # Salvar resultados
        workflow.save_results(resultado)
        
        print(f"\nProcesso concluido com sucesso!")
        print(f"Tema processado: {tema}")
        print(f"Titulo gerado: {resultado['conteudo']['titulo']}")
        print(f"Fontes encontradas: {len(resultado['conteudo']['fontes'])}")
        
    except Exception as e:
        print(f"Erro durante execucao: {e}")
        raise

if __name__ == "__main__":
    main()
