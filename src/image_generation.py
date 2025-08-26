import os
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
from PIL import Image
from openai import OpenAI


class ImageGeneratorTool:
    """Ferramenta para geração de imagens usando o endpoint de imagens da OpenAI"""

    def __init__(self) -> None:
        self.name = "image_generator"
        self.client = OpenAI()
        self.image_model = os.getenv("IMAGE_MODEL", "gpt-image-1")
        self.image_size = os.getenv("IMAGE_SIZE", "1536x1024")

    def generate_image(
        self,
        titulo: str,
        elementos: Optional[List[str]] = None,
        estilo_imagem: str = "realista",
        save_to_temp: bool = True,
        size: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            prompt = self._create_image_prompt(titulo, elementos, estilo_imagem)
            model_to_use = self.image_model
            allowed_gpt_image1 = {"1024x1024", "1024x1536", "1536x1024", "auto"}
            size_to_use = size or self.image_size
            if model_to_use == "gpt-image-1" and size_to_use not in allowed_gpt_image1:
                size_to_use = "1536x1024"
            try:
                extra_args: Dict[str, Any] = {}
                if model_to_use == "gpt-image-1":
                    extra_args["response_format"] = "b64_json"
                response = self.client.images.generate(
                    model=model_to_use,
                    prompt=prompt,
                    size=size_to_use,
                    n=1,
                    **extra_args,
                )
            except Exception as e:  # pragma: no cover - fallback logic
                err_msg = str(e)
                print(f"Erro com {model_to_use}: {err_msg}")
                if model_to_use == "gpt-image-1":
                    allowed_dalle3 = {"1024x1024", "1024x1792", "1792x1024"}
                    size_for_dalle3 = size or self.image_size
                    size_for_dalle3 = (
                        size_for_dalle3 if size_for_dalle3 in allowed_dalle3 else "1792x1024"
                    )
                    response = self.client.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        size=size_for_dalle3,
                        n=1,
                    )
                    model_to_use = "dall-e-3"
                else:
                    raise

            data0 = response.data[0]
            image_path: Optional[str] = None
            image_url: Optional[str] = None
            output_dir = "output/tmp" if save_to_temp else "output"
            if hasattr(data0, "b64_json") and data0.b64_json:
                image_path = self._save_b64_image(data0.b64_json, titulo, output_dir=output_dir)
            elif hasattr(data0, "url") and data0.url:
                image_url = data0.url
                image_path = self._download_and_save_image(image_url, titulo, output_dir=output_dir)
            else:
                raise ValueError("Resposta da API de imagens sem b64_json ou url")

            import os as _os

            _filename = _os.path.basename(image_path) if image_path else None
            public_url = f"/temp/{_filename}" if save_to_temp and _filename else None

            result: Dict[str, Any] = {
                "url": image_url,
                "local_path": image_path,
                "public_url": public_url,
                "prompt_usado": prompt,
                "modelo": model_to_use,
                "tamanho": size_to_use,
                "data_geracao": datetime.now().isoformat(),
            }
            return result
        except Exception as e:
            err = str(e)
            print(f"Erro ao gerar imagem: {err}")
            return {"error": err}

    def _create_image_prompt(
        self,
        titulo: str,
        elementos: Optional[List[str]] = None,
        estilo_imagem: str = "realista",
    ) -> str:
        estilos_keywords = {
            "realista": "fotografia realista, iluminação natural, alto detalhamento, foco nítido",
            "ilustracao": "ilustração digital, traço limpo, paleta equilibrada",
            "abstrato": "abstrato, formas geométricas, composição elegante",
            "criativo": "estilo criativo, composição inovadora, visual impactante",
        }
        base_prompt = (
            "Crie uma imagem científica ou realista que ilustre com precisão o tema proposto. "
            "A imagem deve ter um OVERLAY na parte INFERIOR (faixa/banda) com sombra/gradiente escuro semi-transparente, "
            "e sobre esse overlay posicione o texto do TÍTULO de forma centralizada e altamente legível. "
            "O texto deve ser exatamente o seguinte, entre parênteses: ("
            + titulo
            + "). "
            "Todo o texto inserido DEVE estar em português do Brasil (pt-BR), incluindo o título. "
            "Use tipografia forte, alto contraste e garanta legibilidade do texto sobre o overlay com sombra. "
            "Evite posicionar texto nas bordas externas; utilize margens seguras. "
            "O enquadramento deve ser adequado para redes sociais, com composição limpa e profissional."
        )
        if elementos:
            elementos_text = ", ".join(elementos[:5])
            base_prompt += f" Elementos científicos/realistas importantes a incluir: {elementos_text}."
        style_keywords = estilos_keywords.get(estilo_imagem, estilos_keywords["realista"])
        technical_guidelines = (
            f" Estilo: {style_keywords}. "
            "Manter aparência científica/realista, iluminação equilibrada, ruído mínimo e alta nitidez."
        )
        return base_prompt + technical_guidelines

    def _download_and_save_image(self, image_url: str, titulo: str, output_dir: str = "output") -> str:
        try:
            os.makedirs(output_dir, exist_ok=True)
            import re

            filename = re.sub(r"[^\w\s-]", "", titulo)
            filename = filename.replace(" ", "_").replace("-", "_")
            filename = filename[:50] if len(filename) > 50 else filename
            filename = f"{filename}_image.jpg"
            filepath = os.path.join(output_dir, filename)

            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            if len(response.content) == 0:
                raise Exception("Conteúdo da imagem vazio")

            from io import BytesIO

            image = Image.open(BytesIO(response.content))
            if image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                if image.mode == "RGBA":
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image)
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

            image.save(filepath, "JPEG", quality=95, optimize=True)
            if os.path.exists(filepath):
                if os.path.getsize(filepath) == 0:
                    raise Exception("Arquivo salvo com 0 bytes")
            return filepath
        except Exception as e:  # pragma: no cover - difícil de simular
            print(f"Erro ao salvar imagem (base64): {e}")
            raise

    def _save_b64_image(self, b64_data: str, titulo: str, output_dir: str = "output") -> str:
        try:
            import re
            import base64
            from io import BytesIO

            os.makedirs(output_dir, exist_ok=True)
            filename = re.sub(r"[^\w\s-]", "", titulo)
            filename = filename.replace(" ", "_").replace("-", "_")
            filename = filename[:50] if len(filename) > 50 else filename
            filename = f"{filename}_image.jpg"
            filepath = os.path.join(output_dir, filename)

            img_bytes = base64.b64decode(b64_data)
            image = Image.open(BytesIO(img_bytes))
            if image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                if image.mode == "RGBA":
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image)
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

            image.save(filepath, "JPEG", quality=95, optimize=True)
            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                raise Exception("Falha ao salvar a imagem em disco")
            return filepath
        except Exception as e:  # pragma: no cover - difícil de simular
            print(f"Erro ao salvar imagem (b64): {e}")
            raise


class PexelsImageTool:
    """Ferramenta para buscar imagens no Pexels pela palavra-chave (tema)."""

    BASE_URL = "https://api.pexels.com/v1/search"

    def __init__(self) -> None:
        self.api_key = os.getenv("PEXELS_API_KEY")
        if not self.api_key:
            raise Exception("PEXELS_API_KEY não configurada no ambiente")

    @staticmethod
    def size_to_orientation(size: Optional[str]) -> str:
        s = (size or "").strip().lower()
        if s in {"1024x1536", "1080x1440", "720x1280"}:
            return "portrait"
        if s in {"1536x1024", "1920x1080", "1280x720"}:
            return "landscape"
        return "square"

    def fetch_image(self, tema: str, size: Optional[str] = None, per_page: int = 1) -> Dict[str, Any]:
        headers = {"Authorization": self.api_key}
        params = {
            "query": tema,
            "per_page": max(1, min(per_page, 10)),
            "page": 1,
            "orientation": self.size_to_orientation(size),
        }
        resp = requests.get(self.BASE_URL, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        photos = data.get("photos", [])
        if not photos:
            return {"error": "Nenhuma imagem encontrada no Pexels para o tema informado."}
        photo = photos[0]
        orient = params["orientation"]
        src = photo.get("src", {})
        url = src.get("large")
        if orient == "portrait":
            url = src.get("portrait") or src.get("large") or src.get("original")
        elif orient == "landscape":
            url = src.get("landscape") or src.get("large") or src.get("original")
        else:
            url = src.get("square") or src.get("large") or src.get("original")
        if not url:
            return {"error": "Imagem do Pexels sem URL utilizável."}

        local_path = ImageGeneratorTool()._download_and_save_image(
            url, titulo=tema, output_dir="output/tmp"
        )
        import os as _os

        filename = _os.path.basename(local_path)
        public_url = f"/temp/{filename}"
        return {
            "source": "pexels",
            "local_path": local_path,
            "public_url": public_url,
            "absolute_public_url": None,
            "url": url,
            "photographer": photo.get("photographer"),
            "photographer_url": photo.get("photographer_url"),
            "pexels_page_url": photo.get("url"),
            "orientation": orient,
            "tema": tema,
            "tamanho": size or "",
            "data_geracao": datetime.now().isoformat(),
        }
