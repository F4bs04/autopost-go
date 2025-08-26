#!/usr/bin/env python3
"""
Script de inicialização para Railway
Garante que a aplicação inicie corretamente com as configurações adequadas
"""

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    host = "0.0.0.0"
    
    print(f"🚀 Iniciando servidor na porta {port}")
    print(f"🌐 Host: {host}")
    print("📍 Health check: /api/health")
    print("🌍 URL: autopost-go-production.up.railway.app")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
