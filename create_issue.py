#!/usr/bin/env python3
"""
Script para criar uma nova issue no projeto SCRUM
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

async def create_issue():
    """Cria uma nova issue no projeto SCRUM"""
    
    jira_url = os.getenv("JIRA_URL")
    username = os.getenv("JIRA_USERNAME") 
    api_token = os.getenv("JIRA_API_TOKEN")
    
    print("🎯 CRIANDO NOVA ISSUE NO PROJETO SCRUM")
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
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # 1. Primeiro, buscar informações do projeto SCRUM
        print("1️⃣ Buscando informações do projeto SCRUM...")
        try:
            project_response = await client.get(
                f"{jira_url}/rest/api/3/project/SCRUM",
                headers=headers
            )
            
            print(f"   Status: {project_response.status_code}")
            
            if project_response.status_code == 200:
                project_info = project_response.json()
                print(f"   ✅ Projeto encontrado: {project_info.get('name')}")
                print(f"   Chave: {project_info.get('key')}")
                project_key = project_info.get('key')
            else:
                print(f"   ❌ Erro ao buscar projeto: {project_response.text}")
                # Tentar com chave genérica
                project_key = "SCRUM"
                
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
            project_key = "SCRUM"
        
        print()
        
        # 2. Buscar tipos de issue disponíveis
        print("2️⃣ Buscando tipos de issue...")
        try:
            issue_types_response = await client.get(
                f"{jira_url}/rest/api/3/issuetype",
                headers=headers
            )
            
            print(f"   Status: {issue_types_response.status_code}")
            
            if issue_types_response.status_code == 200:
                issue_types = issue_types_response.json()
                print(f"   ✅ Tipos de issue encontrados: {len(issue_types)}")
                
                # Procurar por tipos comuns (excluindo subtarefas)
                task_type = None
                story_type = None
                bug_type = None
                valid_types = []
                
                for issue_type in issue_types:
                    name = issue_type.get('name', '').lower()
                    is_subtask = issue_type.get('subtask', False)
                    
                    # Pular subtarefas
                    if is_subtask or 'subtask' in name or 'sub-task' in name:
                        print(f"   Pulando subtarefa: {issue_type.get('name')}")
                        continue
                    
                    valid_types.append(issue_type)
                    
                    if 'task' in name and not is_subtask:
                        task_type = issue_type
                    elif 'story' in name:
                        story_type = issue_type
                    elif 'bug' in name:
                        bug_type = issue_type
                
                # Escolher o tipo (prioridade: Task > Story > Bug > Primeiro válido disponível)
                selected_type = task_type or story_type or bug_type or (valid_types[0] if valid_types else issue_types[0])
                print(f"   Tipo selecionado: {selected_type.get('name')} (ID: {selected_type.get('id')})")
                
            else:
                print(f"   ❌ Erro ao buscar tipos: {issue_types_response.text}")
                # Usar ID genérico para Task
                selected_type = {"id": "10001", "name": "Task"}
                
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
            selected_type = {"id": "10001", "name": "Task"}
        
        print()
        
        # 3. Criar a issue
        print("3️⃣ Criando nova issue...")
        
        issue_data = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": "Issue criada via API - Teste de Integração",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Esta issue foi criada automaticamente via API REST do JIRA para testar a integração com o sistema MCP."
                                }
                            ]
                        },
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Detalhes:"
                                }
                            ]
                        },
                        {
                            "type": "bulletList",
                            "content": [
                                {
                                    "type": "listItem",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": "Criada via Python script"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "listItem",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": "Integração MCP-JIRA funcionando"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "listItem",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": "Autenticação via API Token"
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {
                    "id": selected_type.get('id')
                }
            }
        }
        
        try:
            create_response = await client.post(
                f"{jira_url}/rest/api/3/issue",
                headers=headers,
                json=issue_data
            )
            
            print(f"   Status: {create_response.status_code}")
            
            if create_response.status_code == 201:
                created_issue = create_response.json()
                issue_key = created_issue.get('key')
                issue_id = created_issue.get('id')
                
                print(f"   ✅ ISSUE CRIADA COM SUCESSO!")
                print(f"   Chave da Issue: {issue_key}")
                print(f"   ID da Issue: {issue_id}")
                print(f"   URL: {jira_url}/browse/{issue_key}")
                
                # Salvar informações da issue em arquivo
                issue_info = {
                    "key": issue_key,
                    "id": issue_id,
                    "url": f"{jira_url}/browse/{issue_key}",
                    "summary": "Issue criada via API - Teste de Integração",
                    "project": project_key,
                    "type": selected_type.get('name'),
                    "created_at": "2025-09-17T02:15:43Z"
                }
                
                with open("created_issue_info.json", "w", encoding="utf-8") as f:
                    json.dump(issue_info, f, indent=2, ensure_ascii=False)
                
                print(f"   📄 Informações salvas em: created_issue_info.json")
                
                return issue_key, issue_id
                
            else:
                print(f"   ❌ Erro ao criar issue: {create_response.text}")
                return None, None
                
        except Exception as e:
            print(f"   ❌ Exceção ao criar issue: {e}")
            return None, None

if __name__ == "__main__":
    asyncio.run(create_issue())