#!/usr/bin/env python3
"""
Script de debug para verificar conexão e permissões do JIRA
"""

import asyncio
import base64
import json
import os
from dotenv import load_dotenv
import httpx

# Carregar variáveis de ambiente
env_path = os.path.join("docker", ".env")
load_dotenv(env_path)

async def debug_jira():
    """Debug da conexão com JIRA"""
    
    jira_url = os.getenv("JIRA_URL", "")
    jira_username = os.getenv("JIRA_USERNAME", "")
    jira_api_token = os.getenv("JIRA_API_TOKEN", "")
    
    print("🔍 Debug JIRA Connection")
    print("=" * 50)
    print(f"JIRA URL: {jira_url}")
    print(f"Username: {jira_username}")
    print(f"API Token: {'*' * len(jira_api_token) if jira_api_token else 'NÃO CONFIGURADO'}")
    print()
    
    if not all([jira_url, jira_username, jira_api_token]):
        print("❌ Credenciais não configuradas!")
        return
    
    # Preparar autenticação
    auth_string = f"{jira_username}:{jira_api_token}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        # Teste 1: Verificar se consegue conectar
        print("🔗 Teste 1: Verificando conexão...")
        try:
            myself_response = await client.get(
                f"{jira_url}/rest/api/3/myself",
                headers=headers,
                timeout=30.0
            )
            
            print(f"Status: {myself_response.status_code}")
            if myself_response.status_code == 200:
                user_info = myself_response.json()
                print(f"✅ Conectado como: {user_info.get('displayName')} ({user_info.get('emailAddress')})")
            else:
                print(f"❌ Erro: {myself_response.text}")
                return
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return
        
        # Teste 2: Listar projetos
        print("\n📁 Teste 2: Listando projetos...")
        try:
            projects_response = await client.get(
                f"{jira_url}/rest/api/3/project",
                headers=headers,
                timeout=30.0
            )
            
            print(f"Status: {projects_response.status_code}")
            if projects_response.status_code == 200:
                projects = projects_response.json()
                print(f"Projetos encontrados: {len(projects)}")
                
                if projects:
                    for i, project in enumerate(projects[:5], 1):  # Mostrar até 5 projetos
                        print(f"  {i}. {project['key']} - {project['name']}")
                else:
                    print("⚠️ Nenhum projeto encontrado com /rest/api/3/project")
            else:
                print(f"❌ Erro: {projects_response.text}")
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # Teste 3: Buscar projetos com search
        print("\n🔍 Teste 3: Buscando projetos com search...")
        try:
            search_response = await client.get(
                f"{jira_url}/rest/api/3/project/search",
                headers=headers,
                timeout=30.0
            )
            
            print(f"Status: {search_response.status_code}")
            if search_response.status_code == 200:
                search_result = search_response.json()
                projects = search_result.get('values', [])
                print(f"Projetos encontrados via search: {len(projects)}")
                
                if projects:
                    for i, project in enumerate(projects[:5], 1):  # Mostrar até 5 projetos
                        print(f"  {i}. {project['key']} - {project['name']}")
                else:
                    print("⚠️ Nenhum projeto encontrado com search")
            else:
                print(f"❌ Erro: {search_response.text}")
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # Teste 4: Verificar permissões
        print("\n🔐 Teste 4: Verificando permissões...")
        try:
            permissions_response = await client.get(
                f"{jira_url}/rest/api/3/permissions",
                headers=headers,
                timeout=30.0
            )
            
            print(f"Status: {permissions_response.status_code}")
            if permissions_response.status_code == 200:
                permissions = permissions_response.json()
                print("✅ Permissões obtidas com sucesso")
                
                # Verificar permissões específicas
                create_issues = permissions.get('permissions', {}).get('CREATE_ISSUES')
                if create_issues:
                    print(f"  - Criar Issues: {create_issues.get('havePermission', False)}")
            else:
                print(f"❌ Erro: {permissions_response.text}")
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(debug_jira())