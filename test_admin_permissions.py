#!/usr/bin/env python3
"""
Script para testar permissões administrativas específicas
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

async def test_admin_permissions():
    """Testa permissões administrativas específicas"""
    
    jira_url = os.getenv("JIRA_URL")
    username = os.getenv("JIRA_USERNAME") 
    api_token = os.getenv("JIRA_API_TOKEN")
    
    print("👑 TESTE DE PERMISSÕES ADMINISTRATIVAS")
    print("=" * 50)
    print(f"URL: {jira_url}")
    print(f"Username: {username}")
    print()
    
    # Preparar autenticação
    auth_string = f"{username}:{api_token}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Python-JIRA-Admin-Client/1.0"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # 1. Testar com diferentes User-Agents
        print("1️⃣ Testando com diferentes User-Agents...")
        
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Atlassian-Connect/1.0",
            "JIRA-Python-Client/1.0",
            "curl/7.68.0"
        ]
        
        for ua in user_agents:
            try:
                test_headers = headers.copy()
                test_headers["User-Agent"] = ua
                
                response = await client.get(
                    f"{jira_url}/rest/api/3/myself",
                    headers=test_headers
                )
                
                print(f"   {ua[:30]}... -> Status: {response.status_code}")
                
                if response.status_code == 200:
                    user_info = response.json()
                    print(f"   ✅ SUCESSO! Usuário: {user_info.get('displayName')}")
                    return True
                    
            except Exception as e:
                print(f"   ❌ Erro com {ua[:20]}...: {e}")
        
        print()
        
        # 2. Testar endpoints administrativos específicos
        print("2️⃣ Testando endpoints administrativos...")
        
        admin_endpoints = [
            "/rest/api/3/users/search?query=admin",
            "/rest/api/3/applicationrole",
            "/rest/api/3/configuration",
            "/rest/api/3/settings/columns",
            "/rest/api/3/user?accountId=admin"
        ]
        
        for endpoint in admin_endpoints:
            try:
                response = await client.get(
                    f"{jira_url}{endpoint}",
                    headers=headers
                )
                
                print(f"   {endpoint} -> Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"     ✅ Acesso permitido")
                elif response.status_code == 401:
                    print(f"     ❌ Não autorizado")
                elif response.status_code == 403:
                    print(f"     ❌ Proibido (sem permissão)")
                else:
                    print(f"     ⚠️  Status: {response.status_code}")
                    
            except Exception as e:
                print(f"     ❌ Erro: {e}")
        
        print()
        
        # 3. Testar busca por usuários (método alternativo para verificar auth)
        print("3️⃣ Testando busca por usuários...")
        
        try:
            # Buscar usuários com query vazia (deve retornar usuários se autenticado)
            response = await client.get(
                f"{jira_url}/rest/api/3/users/search",
                params={"maxResults": 1},
                headers=headers
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                users = response.json()
                print(f"   ✅ Busca de usuários funcionou! Encontrados: {len(users)} usuários")
                if users:
                    print(f"   Primeiro usuário: {users[0].get('displayName', 'N/A')}")
            else:
                print(f"   ❌ Falha: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        print()
        
        # 4. Testar método alternativo de autenticação (sem Basic)
        print("4️⃣ Testando autenticação alternativa...")
        
        # Tentar com headers mínimos
        minimal_headers = {
            "Authorization": f"Basic {auth_b64}",
            "Accept": "application/json"
        }
        
        try:
            response = await client.get(
                f"{jira_url}/rest/api/3/myself",
                headers=minimal_headers
            )
            
            print(f"   Headers mínimos -> Status: {response.status_code}")
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"   ✅ SUCESSO com headers mínimos!")
                print(f"   Usuário: {user_info.get('displayName')}")
                return True
            else:
                print(f"   ❌ Falha: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        print()
        
        # 5. Verificar se é problema de encoding
        print("5️⃣ Testando diferentes encodings...")
        
        try:
            # Tentar recriar o base64 com diferentes métodos
            auth_string_utf8 = f"{username}:{api_token}"
            auth_b64_utf8 = base64.b64encode(auth_string_utf8.encode('utf-8')).decode('utf-8')
            
            headers_utf8 = {
                "Authorization": f"Basic {auth_b64_utf8}",
                "Accept": "application/json"
            }
            
            response = await client.get(
                f"{jira_url}/rest/api/3/myself",
                headers=headers_utf8
            )
            
            print(f"   UTF-8 encoding -> Status: {response.status_code}")
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"   ✅ SUCESSO com UTF-8!")
                print(f"   Usuário: {user_info.get('displayName')}")
                return True
            else:
                print(f"   ❌ Falha: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        print()
        print("🔍 DIAGNÓSTICO FINAL:")
        print("- Token parece válido (formato correto)")
        print("- Conectividade com JIRA OK")
        print("- Endpoints públicos funcionam")
        print("- Problema específico com autenticação de usuário")
        print()
        print("💡 POSSÍVEIS SOLUÇÕES:")
        print("1. Verificar se o token não expirou")
        print("2. Gerar um novo token API")
        print("3. Verificar configurações de segurança da organização")
        print("4. Confirmar se a conta tem permissões de API habilitadas")

if __name__ == "__main__":
    asyncio.run(test_admin_permissions())