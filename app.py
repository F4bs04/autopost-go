from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from starlette.concurrency import run_in_threadpool
from starlette.responses import FileResponse
import os
from datetime import datetime

from src.agente_ia import ResearchWorkflow, ContentGeneratorAgent, ImageGeneratorTool

app = FastAPI(
    title="Clio Agent API",
    description="API para geração de conteúdo e imagens usando IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Adicionar logs de inicialização
@app.on_event("startup")
async def startup_event():
    print("🚀 Clio Agent API iniciando...")
    print(f"📍 Health check disponível em: /api/health")
    print(f"📚 Documentação em: /docs")

# CORS configurado para frontends externos
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
os.makedirs("frontend", exist_ok=True)

# Servir arquivos estáticos
app.mount("/output", StaticFiles(directory="output"), name="output")
app.mount("/static", StaticFiles(directory="frontend"), name="frontend_static")


# Modelos de dados para a API
class GenerateRequest(BaseModel):
    tema: str
    gerar_imagem: Optional[bool] = True
    estilo_imagem: Optional[str] = "realista"
    
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


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
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
            result = workflow.run(req.tema, generate_image=req.gerar_imagem, estilo_imagem=req.estilo_imagem)
            workflow.save_results(result)
            return result

        result = await run_in_threadpool(run_workflow)

        # Ajustar caminho da imagem para ser acessível via /output
        content = result.get("conteudo", {})
        img = content.get("imagem")
        if img and img.get("local_path"):
            # Normalizar para URL pública
            local_path = img["local_path"]
            # Se o caminho for relativo dentro de output/, expor como /output/<file>
            filename = os.path.basename(local_path)
            img["public_url"] = f"/output/{filename}"

        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro na geração: {str(e)}")
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
async def regenerate_image(req: RegenerateImageRequest):
    """Regenera apenas a imagem a partir do título (opcionalmente usando o tema como elemento)."""
    try:
        tool = ImageGeneratorTool()

        def run_only_image():
            elementos = [req.tema] if req.tema else None
            img = tool.generate_image(titulo=req.titulo, elementos=elementos, estilo_imagem=req.estilo_imagem)
            if img and img.get("local_path"):
                filename = os.path.basename(img["local_path"])
                img["public_url"] = f"/output/{filename}"
                return {"imagem": img}
            return {"imagem": None, "error": "Falha ao gerar imagem. Verifique a chave OPENAI_API_KEY e permissões do modelo."}

        result = await run_in_threadpool(run_only_image)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar imagem: {str(e)}")
