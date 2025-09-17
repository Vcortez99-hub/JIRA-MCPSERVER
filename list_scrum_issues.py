#!/usr/bin/env python3
"""
Script para listar issues do projeto SCRUM
"""

import asyncio
import base64
import httpx
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
env_path = os.path.join("docker", ".env")
load_dotenv(env_path)

async def list_scrum_issues():
    """Lista issues do projeto SCRUM"""
    
    jira_url = os.getenv("JIRA_URL")
    username = os.getenv("JIRA_USERNAME") 
    api_token = os.getenv("JIRA_API_TOKEN")
    
    print("📋 Listando Issues do Projeto SCRUM")
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
    
    async with httpx.AsyncClient() as client:
        
        # 1. Primeiro, testar autenticação básica
        print("1️⃣ Testando autenticação...")
        try:
            auth_response = await client.get(
                f"{jira_url}/rest/api/3/myself",
                headers=headers,
                timeout=30.0
            )
            
            print(f"   Status: {auth_response.status_code}")
            
            if auth_response.status_code == 200:
                user_info = auth_response.json()
                print(f"   ✅ Autenticado como: {user_info.get('displayName')}")
                print(f"   Email: {user_info.get('emailAddress')}")
            else:
                print(f"   ❌ Falha na autenticação: {auth_response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exceção na autenticação: {e}")
            return False
        
        print()
        
        # 2. Buscar issues usando JQL
        print("2️⃣ Buscando issues do projeto SCRUM...")
        
        # Diferentes queries JQL para testar
        jql_queries = [
            "project = SCRUM ORDER BY created DESC",
            "project = SCRUM AND key = SCRUM-40",
            "key = SCRUM-40",
            "project = SCRUM ORDER BY key ASC"
        ]
        
        for i, jql in enumerate(jql_queries, 1):
            try:
                print(f"\n   Query {i}: {jql}")
                
                search_response = await client.get(
                    f"{jira_url}/rest/api/3/search",
                    params={
                        "jql": jql,
                        "maxResults": 10,
                        "fields": "key,summary,status,created,assignee"
                    },
                    headers=headers,
                    timeout=30.0
                )
                
                print(f"   Status: {search_response.status_code}")
                
                if search_response.status_code == 200:
                    search_result = search_response.json()
                    issues = search_result.get('issues', [])
                    total = search_result.get('total', 0)
                    
                    print(f"   ✅ Total de issues encontradas: {total}")
                    
                    if issues:
                        print("   Issues encontradas:")
                        for issue in issues:
                            key = issue.get('key')
                            summary = issue['fields'].get('summary', 'N/A')
                            status = issue['fields'].get('status', {}).get('name', 'N/A')
                            created = issue['fields'].get('created', 'N/A')[:10]  # Só a data
                            assignee = issue['fields'].get('assignee')
                            assignee_name = assignee.get('displayName') if assignee else 'Não atribuído'
                            
                            print(f"     - {key}: {summary}")
                            print(f"       Status: {status} | Criado: {created} | Responsável: {assignee_name}")
                    else:
                        print("   Nenhuma issue encontrada com esta query")
                        
                elif search_response.status_code == 400:
                    error_data = search_response.json()
                    print(f"   ❌ Query inválida: {error_data}")
                    
                elif search_response.status_code == 401:
                    print(f"   ❌ Não autorizado: {search_response.text}")
                    
                else:
                    print(f"   ❌ Erro: {search_response.status_code} - {search_response.text}")
                    
            except Exception as e:
                print(f"   ❌ Exceção na query {i}: {e}")
        
        print()
        
        # 3. Tentar acessar diretamente algumas issues comuns
        print("3️⃣ Testando acesso direto a issues...")
        
        test_issues = ["SCRUM-1", "SCRUM-2", "SCRUM-40", "SCRUM-10"]
        
        for issue_key in test_issues:
            try:
                issue_response = await client.get(
                    f"{jira_url}/rest/api/3/issue/{issue_key}",
                    headers=headers,
                    timeout=30.0
                )
                
                print(f"   {issue_key}: Status {issue_response.status_code}")
                
                if issue_response.status_code == 200:
                    issue_data = issue_response.json()
                    summary = issue_data['fields'].get('summary', 'N/A')
                    status = issue_data['fields'].get('status', {}).get('name', 'N/A')
                    print(f"     ✅ {summary} (Status: {status})")
                    
                elif issue_response.status_code == 404:
                    print(f"     ❌ Issue não encontrada ou sem permissão")
                    
                else:
                    print(f"     ❌ Erro: {issue_response.text}")
                    
            except Exception as e:
                print(f"     ❌ Exceção: {e}")

if __name__ == "__main__":
    asyncio.run(list_scrum_issues())