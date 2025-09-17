#!/usr/bin/env python3
"""
Script para adicionar comentário na issue SCRUM-40
"""

import asyncio
import base64
import httpx
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
env_path = os.path.join("docker", ".env")
load_dotenv(env_path)

async def add_comment_to_scrum40():
    """Adiciona comentário na issue SCRUM-40"""
    
    jira_url = os.getenv("JIRA_URL")
    username = os.getenv("JIRA_USERNAME") 
    api_token = os.getenv("JIRA_API_TOKEN")
    
    print("💬 Adicionando Comentário na Issue SCRUM-40")
    print("=" * 50)
    print(f"URL: {jira_url}")
    print(f"Username: {username}")
    print(f"Token: {api_token[:20]}...{api_token[-10:]}")
    print()
    
    # Preparar autenticação
    auth_string = f"{username}:{api_token}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Comentário a ser adicionado
    comment_text = "Comentário adicionado via MCP JIRA Admin - Teste de integração realizado com sucesso!"
    
    comment_data = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": comment_text
                        }
                    ]
                }
            ]
        }
    }
    
    async with httpx.AsyncClient() as client:
        
        # 1. Primeiro, verificar se a issue existe
        print("1️⃣ Verificando se a issue SCRUM-40 existe...")
        try:
            issue_response = await client.get(
                f"{jira_url}/rest/api/3/issue/SCRUM-40",
                headers=headers,
                timeout=30.0
            )
            
            print(f"   Status: {issue_response.status_code}")
            
            if issue_response.status_code == 200:
                issue_data = issue_response.json()
                print(f"   ✅ Issue encontrada: {issue_data.get('key')} - {issue_data['fields']['summary']}")
                print(f"   Status atual: {issue_data['fields']['status']['name']}")
                
                # 2. Adicionar comentário
                print("\n2️⃣ Adicionando comentário...")
                comment_response = await client.post(
                    f"{jira_url}/rest/api/3/issue/SCRUM-40/comment",
                    headers=headers,
                    json=comment_data,
                    timeout=30.0
                )
                
                print(f"   Status: {comment_response.status_code}")
                
                if comment_response.status_code == 201:
                    comment_result = comment_response.json()
                    print(f"   ✅ Comentário adicionado com sucesso!")
                    print(f"   ID do comentário: {comment_result.get('id')}")
                    print(f"   Autor: {comment_result.get('author', {}).get('displayName')}")
                    print(f"   Data: {comment_result.get('created')}")
                    
                    return True
                    
                elif comment_response.status_code == 401:
                    print(f"   ❌ Erro de autenticação: {comment_response.text}")
                    return False
                    
                elif comment_response.status_code == 403:
                    print(f"   ❌ Sem permissão para comentar: {comment_response.text}")
                    return False
                    
                elif comment_response.status_code == 404:
                    print(f"   ❌ Issue não encontrada: {comment_response.text}")
                    return False
                    
                else:
                    print(f"   ❌ Erro inesperado: {comment_response.status_code}")
                    print(f"   Resposta: {comment_response.text}")
                    return False
                    
            elif issue_response.status_code == 401:
                print(f"   ❌ Erro de autenticação: {issue_response.text}")
                return False
                
            elif issue_response.status_code == 404:
                print(f"   ❌ Issue SCRUM-40 não encontrada: {issue_response.text}")
                return False
                
            else:
                print(f"   ❌ Erro ao buscar issue: {issue_response.status_code}")
                print(f"   Resposta: {issue_response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(add_comment_to_scrum40())
    if success:
        print("\n🎉 Comentário adicionado com sucesso na issue SCRUM-40!")
    else:
        print("\n❌ Falha ao adicionar comentário na issue SCRUM-40")