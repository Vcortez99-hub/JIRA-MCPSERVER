#!/usr/bin/env python3
"""
Teste direto do token JIRA
"""

import asyncio
import base64
import httpx

async def test_token_direct():
    """Teste direto com o token fornecido"""
    
    jira_url = "https://canalrural-devskin.atlassian.net"
    username = "vinicius.cortez03@gmail.com"
    api_token = os.getenv("JIRA_API_TOKEN", "YOUR_API_TOKEN_HERE")
    
    print("🔍 Teste Direto do Token")
    print("=" * 50)
    print(f"URL: {jira_url}")
    print(f"Username: {username}")
    print(f"Token (primeiros 20 chars): {api_token[:20]}...")
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
    
    print(f"Auth Header: Basic {auth_b64[:50]}...")
    print()
    
    async with httpx.AsyncClient() as client:
        try:
            # Teste básico de autenticação
            print("🔗 Testando /rest/api/3/myself...")
            response = await client.get(
                f"{jira_url}/rest/api/3/myself",
                headers=headers,
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                user_info = response.json()
                print("✅ SUCESSO!")
                print(f"Nome: {user_info.get('displayName')}")
                print(f"Email: {user_info.get('emailAddress')}")
                print(f"Account ID: {user_info.get('accountId')}")
                
                # Agora testar projetos
                print("\n📁 Testando projetos...")
                projects_response = await client.get(
                    f"{jira_url}/rest/api/3/project",
                    headers=headers,
                    timeout=30.0
                )
                
                print(f"Projetos Status: {projects_response.status_code}")
                if projects_response.status_code == 200:
                    projects = projects_response.json()
                    print(f"Projetos encontrados: {len(projects)}")
                    
                    if projects:
                        for project in projects[:3]:
                            print(f"  - {project['key']}: {project['name']}")
                    else:
                        print("  Nenhum projeto encontrado")
                        
                        # Tentar com search
                        print("\n🔍 Tentando project/search...")
                        search_response = await client.get(
                            f"{jira_url}/rest/api/3/project/search",
                            headers=headers,
                            timeout=30.0
                        )
                        
                        print(f"Search Status: {search_response.status_code}")
                        if search_response.status_code == 200:
                            search_result = search_response.json()
                            print(f"Search Result: {search_result}")
                else:
                    print(f"Erro nos projetos: {projects_response.text}")
                    
            else:
                print(f"❌ ERRO: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exceção: {e}")

if __name__ == "__main__":
    asyncio.run(test_token_direct())