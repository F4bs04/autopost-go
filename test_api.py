#!/usr/bin/env python3
"""
Script para testar a API diretamente e ver os erros detalhados
"""

import requests
import json

def test_generate_endpoint():
    """Testa o endpoint /api/generate"""
    url = "https://autopost-go-production.up.railway.app/api/generate"
    
    payload = {
        "tema": "inteligência artificial",
        "gerar_imagem": True,
        "estilo_imagem": "realista"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🧪 Testando endpoint /api/generate...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Sucesso!")
            data = response.json()
            print(f"📄 Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print("❌ Erro!")
            print(f"📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"💥 Erro na requisição: {e}")

if __name__ == "__main__":
    test_generate_endpoint()
