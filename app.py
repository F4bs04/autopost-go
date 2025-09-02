from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from starlette.concurrency import run_in_threadpool
from starlette.responses import FileResponse
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
import os
from datetime import datetime, timedelta
import asyncio

from src.agente_ia import ResearchWorkflow, ContentGeneratorAgent, ImageGeneratorTool, PexelsImageTool, FreepikImageGeneratorTool

app = FastAPI(
    title="Clio Agent API",
    description="API para geração de conteúdo e imagens usando IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Adicionar logs de inicialização
cleanup_task = None

@app.on_event("startup")
async def startup_event():
    print("🚀 Clio Agent API iniciando...")
    print(f"📍 Health check disponível em: /api/health")
    print(f"📚 Documentação em: /docs")
    # Iniciar tarefa assíncrona para limpar imagens temporárias
    async def _cleanup_loop():
        while True:
            try:
                cutoff = datetime.now() - timedelta(days=1)
                # Limpeza de imagens temporárias
                base_dir = "output/tmp"
                for fname in os.listdir(base_dir):
                    fpath = os.path.join(base_dir, fname)
                    try:
                        if os.path.isfile(fpath):
                            mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                            if mtime < cutoff:
                                os.remove(fpath)
                    except Exception as _e:
                        # apenas loga; nunca derruba o loop
                        print(f"[cleanup] erro removendo {fpath}: {_e}")

                # Limpeza de textos gerados (JSON/MD) com mais de 24h
                content_dir = "output"
                for fname in os.listdir(content_dir):
                    fpath = os.path.join(content_dir, fname)
                    try:
                        if os.path.isfile(fpath) and (fname.endswith('.json') or fname.endswith('.md')):
                            mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                            if mtime < cutoff:
                                os.remove(fpath)
                    except Exception as _e:
                        print(f"[cleanup] erro removendo conteúdo {fpath}: {_e}")
            except Exception as e:
                print(f"[cleanup] erro no ciclo: {e}")
            # aguarda 1 hora entre limpezas
            await asyncio.sleep(3600)

    global cleanup_task
    cleanup_task = asyncio.create_task(_cleanup_loop())

@app.on_event("shutdown")
async def shutdown_event():
    global cleanup_task
    if cleanup_task:
        cleanup_task.cancel()

# CORS configurado para frontends externos
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Garantir diretórios
os.makedirs("output", exist_ok=True)
os.makedirs("output/tmp", exist_ok=True)  # imagens temporárias (até 24h)
os.makedirs("frontend", exist_ok=True)

# Servir arquivos estáticos
app.mount("/output", StaticFiles(directory="output"), name="output")
app.mount("/temp", StaticFiles(directory="output/tmp"), name="temp")
app.mount("/static", StaticFiles(directory="frontend"), name="frontend_static")


# Modelos de dados para a API
class GenerateRequest(BaseModel):
    tema: str
    gerar_imagem: Optional[bool] = True
    estilo_imagem: Optional[str] = "realista"
    tamanho: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "tema": "inteligência artificial",
                "gerar_imagem": True,
                "estilo_imagem": "realista"
            }
        }

class GenerateResponse(BaseModel):
    tema: str
    data_geracao: str
    conteudo: dict
    workflow_version: str


@app.api_route("/api/test", methods=["GET", "POST", "OPTIONS"])
async def test_openai():
    """Endpoint de teste para verificar se OpenAI está funcionando"""
    try:
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            return {"error": "OPENAI_API_KEY não configurada"}
        
        from openai import OpenAI
        client = OpenAI()
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Diga apenas 'teste ok'"}],
            max_tokens=10
        )
        
        return {
            "status": "success",
            "response": response.choices[0].message.content,
            "key_configured": True
        }
    except Exception as e:
        return {"error": str(e), "key_configured": bool(os.getenv('OPENAI_API_KEY'))}

@app.post("/api/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest, request: Request):
    """Gera conteúdo e imagem a partir de um tema e retorna o JSON completo.
    
    Este endpoint é o principal da API. Ele:
    1. Pesquisa informações sobre o tema na web
    2. Gera conteúdo estruturado usando IA
    3. Opcionalmente gera uma imagem relacionada
    4. Retorna tudo em formato JSON
    """
    try:
        # Verificar se a chave OpenAI está configurada
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise HTTPException(
                status_code=500, 
                detail="OPENAI_API_KEY não configurada. Configure a variável de ambiente no Railway."
            )
        
        workflow = ResearchWorkflow()

        def run_workflow():
            result = workflow.run(req.tema, generate_image=req.gerar_imagem, estilo_imagem=req.estilo_imagem, tamanho=req.tamanho)
            workflow.save_results(result)
            return result

        result = await run_in_threadpool(run_workflow)

        # Garantir imagem: se solicitada e ausente, tenta gerar agora
        content = result.get("conteudo", {})
        img = content.get("imagem")
        if req.gerar_imagem and (not img or not isinstance(img, dict) or not img.get("local_path")):
            try:
                elementos = [result.get("tema")] if result.get("tema") else None
                tool = ImageGeneratorTool()
                new_img = tool.generate_image(
                    titulo=content.get("titulo") or result.get("tema") or "imagem",
                    elementos=elementos,
                    estilo_imagem=req.estilo_imagem,
                    save_to_temp=True,
                    size=req.tamanho
                )
                if isinstance(new_img, dict) and new_img.get("local_path"):
                    content["imagem"] = new_img
                    img = new_img
                elif isinstance(new_img, dict) and new_img.get("error"):
                    content["imagem_error"] = new_img.get("error")
            except Exception as _e:
                content["imagem_error"] = str(_e)

        if img and img.get("local_path"):
            # Se o gerador já definiu public_url (ex.: /temp/...), manter
            if not img.get("public_url"):
                local_path = img["local_path"]
                filename = os.path.basename(local_path)
                norm = os.path.normpath(local_path).replace("\\", "/")
                is_tmp = "/output/tmp/" in norm or norm.endswith("/output/tmp/" + filename) or "/output/tmp" in norm
                rel = f"tmp/{filename}" if is_tmp else filename
                img["public_url"] = f"/output/{rel}"
            # Construir URL absoluta para evitar problemas de CORS em clientes externos
            try:
                base = str(request.base_url).rstrip('/')
                rel = img.get("public_url", "")
                if rel.startswith('/'):
                    img["absolute_public_url"] = f"{base}{rel}"
                else:
                    img["absolute_public_url"] = rel
                # Campo de compatibilidade: 'url' aponta para a URL absoluta local
                img["url"] = img.get("absolute_public_url") or img.get("public_url")
            except Exception:
                pass
            # Remover URL externa do provedor (azure blob) para evitar uso pelo cliente
            if "url" in img:
                # se for diferente da nossa absolute_public_url, substitui
                if img.get("absolute_public_url"):
                    img["url"] = img["absolute_public_url"]
                else:
                    img.pop("url", None)

        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro na geração: {str(e)}")
        print(f"Stack trace: {error_details}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar conteúdo: {str(e)}")


@app.get("/")
async def index():
    """Serve a página principal do frontend."""
    return FileResponse("frontend/index.html")


class RegenerateTextRequest(BaseModel):
    tema: str
    
    class Config:
        schema_extra = {
            "example": {
                "tema": "blockchain"
            }
        }

class RegenerateImageRequest(BaseModel):
    titulo: str
    tema: Optional[str] = None
    estilo_imagem: Optional[str] = "realista"
    tamanho: Optional[str] = None
    fonte: Optional[str] = "openai"  # 'openai' | 'pexels'
    
    class Config:
        schema_extra = {
            "example": {
                "titulo": "O Futuro da Inteligência Artificial",
                "tema": "tecnologia",
                "estilo_imagem": "criativo"
            }
        }

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    endpoints: List[str]

# Endpoints da API

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de health check para monitoramento da API."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        endpoints=[
            "/api/generate",
            "/api/regenerate-text", 
            "/api/regenerate-image",
            "/api/health",
            "/docs"
        ]
    )


@app.get("/api/image-config")
async def image_config():
    """Diagnóstico: retorna a configuração de geração de imagem atualmente em uso (sem segredos).
    Útil para verificar se o serviço está rodando com gpt-image-1 e fallback desabilitado.
    """
    try:
        return {
            "IMAGE_MODEL": os.getenv("IMAGE_MODEL", "gpt-image-1"),
            "DISABLE_IMAGE_FALLBACK": os.getenv("DISABLE_IMAGE_FALLBACK", "true"),
            "IMAGE_SIZE": os.getenv("IMAGE_SIZE", "1536x1024"),
            "PEXELS_CONFIGURED": bool(os.getenv("PEXELS_API_KEY")),
            "FREEPIK_CONFIGURED": bool(os.getenv("FREEPIK_API_KEY")),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler configuração: {str(e)}")

@app.post("/api/regenerate-text")
async def regenerate_text(req: RegenerateTextRequest):
    """Regenera apenas o texto (sem imagem) para um tema."""
    try:
        agent = ContentGeneratorAgent()

        def run_only_text():
            content = agent.generate_structured_content(req.tema, generate_image=False)
            return {"conteudo": content}

        result = await run_in_threadpool(run_only_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar texto: {str(e)}")

@app.post("/api/regenerate-image")
async def regenerate_image(req: RegenerateImageRequest, request: Request):
    """Regenera apenas a imagem a partir do título (opcionalmente usando o tema como elemento)."""
    try:
        # Decide fonte
        fonte = (req.fonte or "openai").lower()
        tool = ImageGeneratorTool() if fonte == "openai" else None

        def run_only_image():
            if fonte == "pexels":
                # Usa tema se houver, senão cai para título como consulta
                query = req.tema or req.titulo
                ptool = PexelsImageTool()
                img = ptool.fetch_image(tema=query, size=req.tamanho)
            elif fonte == "freepik":
                elementos = [req.tema] if req.tema else None
                ftool = FreepikImageGeneratorTool()
                img = ftool.generate_image(
                    titulo=req.titulo,
                    elementos=elementos,
                    estilo_imagem=req.estilo_imagem,
                    save_to_temp=True,
                    size=req.tamanho
                )
            else:
                elementos = [req.tema] if req.tema else None
                img = tool.generate_image(
                    titulo=req.titulo,
                    elementos=elementos,
                    estilo_imagem=req.estilo_imagem,
                    save_to_temp=True,
                    size=req.tamanho
                )
            if img and isinstance(img, dict) and img.get("local_path"):
                # Se já veio com public_url de /temp, mantenha; senão, caia em /output
                if not img.get("public_url"):
                    filename = os.path.basename(img["local_path"])
                    norm = os.path.normpath(img["local_path"]).replace("\\", "/")
                    is_tmp = "/output/tmp/" in norm or norm.endswith("/output/tmp/" + filename) or "/output/tmp" in norm
                    rel = f"tmp/{filename}" if is_tmp else filename
                    img["public_url"] = f"/output/{rel}"
                # Adiciona URL absoluta
                try:
                    base = str(request.base_url).rstrip('/')
                    rel = img.get("public_url", "")
                    if rel.startswith('/'):
                        img["absolute_public_url"] = f"{base}{rel}"
                    else:
                        img["absolute_public_url"] = rel
                    # Campo de compatibilidade: 'url' aponta para a URL absoluta local
                    img["url"] = img.get("absolute_public_url") or img.get("public_url")
                except Exception:
                    pass
                # Remover URL externa do provedor
                if "url" in img and img.get("url") and img.get("absolute_public_url") and img["url"] != img["absolute_public_url"]:
                    img["url"] = img["absolute_public_url"]
                return {"imagem": img}
            return {"imagem": None, "error": "Falha ao gerar imagem. Verifique a chave OPENAI_API_KEY e permissões do modelo."}

        result = await run_in_threadpool(run_only_image)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar imagem: {str(e)}")

@app.post("/api/generate-image")
async def generate_image(req: RegenerateImageRequest, request: Request):
    """Gera apenas a imagem a partir de um título/tema e retorna metadados da imagem.
    O título será incluído como texto dentro da imagem (conforme prompt da ferramenta).
    """
    try:
        # Decide fonte
        fonte = (req.fonte or "openai").lower()
        tool = ImageGeneratorTool() if fonte == "openai" else None

        def run_generate_image():
            if fonte == "pexels":
                query = req.tema or req.titulo
                ptool = PexelsImageTool()
                img = ptool.fetch_image(tema=query, size=req.tamanho)
            elif fonte == "freepik":
                elementos = [req.tema] if req.tema else None
                ftool = FreepikImageGeneratorTool()
                img = ftool.generate_image(
                    titulo=req.titulo,
                    elementos=elementos,
                    estilo_imagem=req.estilo_imagem,
                    save_to_temp=True,
                    size=req.tamanho
                )
            else:
                elementos = [req.tema] if req.tema else None
                img = tool.generate_image(
                    titulo=req.titulo,
                    elementos=elementos,
                    estilo_imagem=req.estilo_imagem,
                    save_to_temp=True,
                    size=req.tamanho
                )
            if img and img.get("local_path"):
                if not img.get("public_url"):
                    local_path = img["local_path"]
                    filename = os.path.basename(local_path)
                    norm = os.path.normpath(local_path).replace("\\", "/")
                    is_tmp = "/output/tmp/" in norm or norm.endswith("/output/tmp/" + filename) or "/output/tmp" in norm
                    rel = f"tmp/{filename}" if is_tmp else filename
                    img["public_url"] = f"/output/{rel}"
                try:
                    base = str(request.base_url).rstrip('/')
                    rel = img.get("public_url", "")
                    if rel.startswith('/'):
                        img["absolute_public_url"] = f"{base}{rel}"
                    else:
                        img["absolute_public_url"] = rel
                    img["url"] = img.get("absolute_public_url") or img.get("public_url")
                except Exception:
                    pass
                if "url" in img and img.get("url") and img.get("absolute_public_url") and img["url"] != img["absolute_public_url"]:
                    img["url"] = img["absolute_public_url"]
                return {"imagem": img}
            return {"imagem": None, "error": "Falha ao gerar imagem. Verifique a chave OPENAI_API_KEY e permissões do modelo."}

        result = await run_in_threadpool(run_generate_image)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar imagem: {str(e)}")


@app.post("/api/generate-pexels-image")
async def generate_pexels_image(req: RegenerateImageRequest, request: Request):
    """Compat: endpoint específico para Pexels usado por alguns frontends externos.
    Força a busca no Pexels e retorna o mesmo formato de resposta dos outros endpoints.
    """
    try:
        def run_generate_pexels():
            query = req.tema or req.titulo
            ptool = PexelsImageTool()
            img = ptool.fetch_image(tema=query, size=req.tamanho)
            if img and isinstance(img, dict) and img.get("local_path"):
                # Garante public_url/absolute_public_url/url normalizados
                if not img.get("public_url"):
                    local_path = img["local_path"]
                    filename = os.path.basename(local_path)
                    norm = os.path.normpath(local_path).replace("\\", "/")
                    is_tmp = "/output/tmp/" in norm or norm.endswith("/output/tmp/" + filename) or "/output/tmp" in norm
                    rel = f"tmp/{filename}" if is_tmp else filename
                    img["public_url"] = f"/output/{rel}"
                try:
                    base = str(request.base_url).rstrip('/')
                    rel = img.get("public_url", "")
                    if rel.startswith('/'):
                        img["absolute_public_url"] = f"{base}{rel}"
                    else:
                        img["absolute_public_url"] = rel
                    img["url"] = img.get("absolute_public_url") or img.get("public_url")
                except Exception:
                    pass
                # Se 'url' ainda aponta para a URL externa do provedor, substitui pela absoluta local
                if (
                    "url" in img and img.get("url") and img.get("absolute_public_url") and
                    img["url"] != img["absolute_public_url"]
                ):
                    img["url"] = img["absolute_public_url"]
                return {
                    "imagem": img,
                    "image": img,  # compat
                    "url": img.get("url"),
                    "public_url": img.get("public_url"),
                    "absolute_public_url": img.get("absolute_public_url"),
                    "source": "pexels",
                    "success": True,
                }
            return {
                "imagem": None,
                "image": None,
                "error": "Falha ao gerar imagem via Pexels.",
                "message": "Falha ao gerar imagem via Pexels.",
                "source": "pexels",
                "success": False,
            }

        result = await run_in_threadpool(run_generate_pexels)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar imagem (Pexels): {str(e)}")
