#!/usr/bin/env python3
"""
Teste específico de permissões JIRA
"""

import asyncio
import base64
import httpx
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
env_path = os.path.join("docker", ".env")
load_dotenv(env_path)

async def test_jira_permissions():
    """Teste detalhado de permissões"""
    
    jira_url = os.getenv("JIRA_URL")
    username = os.getenv("JIRA_USERNAME") 
    api_token = os.getenv("JIRA_API_TOKEN")
    
    print("🔍 Teste Detalhado de Permissões JIRA")
    print("=" * 60)
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
        
        # 1. Teste de autenticação básica
        print("1️⃣ Testando autenticação básica...")
        try:
            response = await client.get(
                f"{jira_url}/rest/api/3/myself",
                headers=headers,
                timeout=30.0
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                user_info = response.json()
                print(f"   ✅ Usuário autenticado: {user_info.get('displayName')}")
                print(f"   Account ID: {user_info.get('accountId')}")
                print(f"   Email: {user_info.get('emailAddress')}")
            else:
                print(f"   ❌ Erro: {response.text}")
                return
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
            return
        
        print()
        
        # 2. Teste de permissões gerais
        print("2️⃣ Testando permissões gerais...")
        try:
            perm_response = await client.get(
                f"{jira_url}/rest/api/3/mypermissions",
                headers=headers,
                timeout=30.0
            )
            
            print(f"   Status: {perm_response.status_code}")
            if perm_response.status_code == 200:
                permissions = perm_response.json()
                print(f"   ✅ Permissões obtidas: {len(permissions.get('permissions', {}))}")
                
                # Verificar permissões específicas
                perms = permissions.get('permissions', {})
                important_perms = ['BROWSE_PROJECTS', 'CREATE_ISSUES', 'EDIT_ISSUES']
                
                for perm in important_perms:
                    if perm in perms:
                        has_perm = perms[perm].get('havePermission', False)
                        print(f"   {perm}: {'✅' if has_perm else '❌'}")
            else:
                print(f"   ❌ Erro: {perm_response.text}")
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
        
        print()
        
        # 3. Teste de projetos com diferentes endpoints
        print("3️⃣ Testando acesso a projetos...")
        
        endpoints = [
            "/rest/api/3/project",
            "/rest/api/3/project/search", 
            "/rest/api/3/project/search?expand=description,lead,url,projectKeys",
            "/rest/api/2/project"  # API v2 como fallback
        ]
        
        for endpoint in endpoints:
            try:
                print(f"   Testando: {endpoint}")
                proj_response = await client.get(
                    f"{jira_url}{endpoint}",
                    headers=headers,
                    timeout=30.0
                )
                
                print(f"   Status: {proj_response.status_code}")
                
                if proj_response.status_code == 200:
                    projects_data = proj_response.json()
                    
                    if isinstance(projects_data, list):
                        projects = projects_data
                    elif isinstance(projects_data, dict) and 'values' in projects_data:
                        projects = projects_data['values']
                    else:
                        projects = []
                    
                    print(f"   ✅ Projetos encontrados: {len(projects)}")
                    
                    if projects:
                        for i, project in enumerate(projects[:3]):
                            key = project.get('key', 'N/A')
                            name = project.get('name', 'N/A')
                            print(f"     {i+1}. {key}: {name}")
                        
                        # Se encontrou projetos, testar acesso direto ao SCRUM
                        if any(p.get('key') == 'SCRUM' for p in projects):
                            print("   🎯 Projeto SCRUM encontrado na lista!")
                        else:
                            print("   ⚠️ Projeto SCRUM não encontrado na lista")
                            print("   Projetos disponíveis:")
                            for project in projects:
                                print(f"     - {project.get('key')}: {project.get('name')}")
                else:
                    print(f"   ❌ Erro: {proj_response.text}")
                    
            except Exception as e:
                print(f"   ❌ Exceção: {e}")
            
            print()
        
        # 4. Teste direto do projeto SCRUM
        print("4️⃣ Testando acesso direto ao projeto SCRUM...")
        try:
            scrum_response = await client.get(
                f"{jira_url}/rest/api/3/project/SCRUM",
                headers=headers,
                timeout=30.0
            )
            
            print(f"   Status: {scrum_response.status_code}")
            if scrum_response.status_code == 200:
                scrum_project = scrum_response.json()
                print(f"   ✅ Projeto SCRUM acessível: {scrum_project.get('name')}")
            else:
                print(f"   ❌ Projeto SCRUM não acessível: {scrum_response.text}")
        except Exception as e:
            print(f"   ❌ Exceção: {e}")

if __name__ == "__main__":
    asyncio.run(test_jira_permissions())