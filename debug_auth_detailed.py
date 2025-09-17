#!/usr/bin/env python3
"""
Script de debug detalhado para investigar problemas de autenticação JIRA
"""

import asyncio
import base64
import httpx
import os
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
env_path = os.path.join("docker", ".env")
load_dotenv(env_path)

async def debug_auth():
    """Debug detalhado da autenticação JIRA"""
    
    jira_url = os.getenv("JIRA_URL")
    username = os.getenv("JIRA_USERNAME") 
    api_token = os.getenv("JIRA_API_TOKEN")
    
    print("🔍 DEBUG DETALHADO - Autenticação JIRA")
    print("=" * 60)
    print(f"URL: {jira_url}")
    print(f"Username: {username}")
    print(f"Token (primeiros 20 chars): {api_token[:20]}...")
    print(f"Token (últimos 10 chars): ...{api_token[-10:]}")
    print(f"Tamanho do token: {len(api_token)} caracteres")
    print()
    
    # Verificar se o token parece válido (formato Atlassian)
    if api_token.startswith("ATATT3xFfGF0"):
        print("✅ Token parece ter formato válido do Atlassian")
    else:
        print("⚠️  Token não parece ter formato padrão do Atlassian")
    
    print()
    
    # Preparar diferentes tipos de autenticação para teste
    auth_string = f"{username}:{api_token}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    print(f"String de auth: {username}:[TOKEN]")
    print(f"Auth base64 (primeiros 30 chars): {auth_b64[:30]}...")
    print()
    
    headers_basic = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Python-JIRA-Client/1.0"
    }
    
    # Testar também com Bearer token (caso seja esse o formato esperado)
    headers_bearer = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Python-JIRA-Client/1.0"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # 1. Teste com Basic Auth
        print("1️⃣ Testando Basic Authentication...")
        try:
            response = await client.get(
                f"{jira_url}/rest/api/3/myself",
                headers=headers_basic
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Headers de resposta: {dict(response.headers)}")
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"   ✅ Sucesso! Usuário: {user_info.get('displayName')}")
                print(f"   Email: {user_info.get('emailAddress')}")
                print(f"   Account ID: {user_info.get('accountId')}")
                return True
            else:
                print(f"   ❌ Falha: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
        
        print()
        
        # 2. Teste com Bearer Token (caso seja necessário)
        print("2️⃣ Testando Bearer Token...")
        try:
            response = await client.get(
                f"{jira_url}/rest/api/3/myself",
                headers=headers_bearer
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"   ✅ Sucesso com Bearer! Usuário: {user_info.get('displayName')}")
                return True
            else:
                print(f"   ❌ Falha: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
        
        print()
        
        # 3. Testar endpoints alternativos
        print("3️⃣ Testando endpoints alternativos...")
        
        endpoints = [
            "/rest/api/2/myself",  # API v2
            "/rest/api/3/serverInfo",  # Info do servidor
            "/rest/api/3/permissions",  # Permissões
            "/rest/api/2/serverInfo"   # Info do servidor v2
        ]
        
        for endpoint in endpoints:
            try:
                print(f"   Testando: {endpoint}")
                response = await client.get(
                    f"{jira_url}{endpoint}",
                    headers=headers_basic
                )
                
                print(f"     Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"     ✅ Sucesso!")
                    if endpoint.endswith("serverInfo"):
                        server_info = response.json()
                        print(f"     Versão JIRA: {server_info.get('version', 'N/A')}")
                        print(f"     Tipo: {server_info.get('deploymentType', 'N/A')}")
                elif response.status_code == 401:
                    print(f"     ❌ 401 - Não autorizado")
                elif response.status_code == 403:
                    print(f"     ❌ 403 - Proibido")
                else:
                    print(f"     ❌ {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                print(f"     ❌ Exceção: {e}")
        
        print()
        
        # 4. Teste de conectividade básica
        print("4️⃣ Testando conectividade básica...")
        try:
            response = await client.get(jira_url)
            print(f"   Status da página inicial: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Conectividade OK")
            else:
                print(f"   ⚠️  Status inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro de conectividade: {e}")
        
        print()
        
        # 5. Informações de debug adicionais
        print("5️⃣ Informações adicionais de debug...")
        print(f"   URL completa da API: {jira_url}/rest/api/3/myself")
        print(f"   Formato esperado do token: ATATT3xFfGF0...")
        print(f"   Seu token começa com: {api_token[:12]}...")
        
        # Verificar se há caracteres especiais problemáticos
        if any(char in api_token for char in [' ', '\n', '\r', '\t']):
            print("   ⚠️  ATENÇÃO: Token contém espaços ou quebras de linha!")
        else:
            print("   ✅ Token não contém caracteres problemáticos visíveis")

if __name__ == "__main__":
    asyncio.run(debug_auth())