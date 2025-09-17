#!/usr/bin/env python3
"""
Servidor MCP simples para JIRA Admin
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

# Carregar variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    # Procurar o arquivo .env no diretório docker
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docker", ".env")
    load_dotenv(env_path)
except ImportError:
    print("⚠️ python-dotenv não instalado. Instale com: pip install python-dotenv")

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleJiraMCP:
    def __init__(self):
        # Configurações do JIRA
        self.jira_url = os.getenv("JIRA_URL", "")
        self.jira_username = os.getenv("JIRA_USERNAME", "")
        self.jira_api_token = os.getenv("JIRA_API_TOKEN", "")
        self.org_id = os.getenv("ORG_ID", "")
        
        # Servidor MCP
        self.server = Server("jira-admin-mcp")
        self._setup_handlers()
        
        logger.info("Servidor MCP JIRA Admin inicializado")

    def _setup_handlers(self):
        """Configura os handlers do servidor MCP"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """Lista as ferramentas disponíveis"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="test_connection",
                        description="Testa a conexão com o JIRA",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    ),
                    Tool(
                        name="get_user_info",
                        description="Obtém informações de um usuário",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "username": {
                                    "type": "string",
                                    "description": "Nome de usuário ou email"
                                }
                            },
                            "required": ["username"]
                        }
                    ),
                    Tool(
                        name="create_test_issue",
                        description="Cria um issue de teste no JIRA para demonstração",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "summary": {
                                    "type": "string",
                                    "description": "Título/resumo do issue"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Descrição detalhada do issue",
                                    "default": "Issue criado via MCP JIRA Admin"
                                }
                            },
                            "required": ["summary"]
                        }
                    )
                ]
            )

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            """Executa uma ferramenta"""
            try:
                if request.name == "test_connection":
                    result = await self._test_connection()
                elif request.name == "get_user_info":
                    result = await self._get_user_info(request.arguments)
                elif request.name == "create_test_issue":
                    result = await self._create_test_issue(request.arguments)
                else:
                    raise ValueError(f"Ferramenta desconhecida: {request.name}")
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                )
            except Exception as e:
                logger.error(f"Erro ao executar ferramenta {request.name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Erro: {str(e)}")],
                    isError=True
                )

    async def _test_connection(self) -> Dict[str, Any]:
        """Testa a conexão com o JIRA"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.jira_url}/rest/api/3/myself",
                    auth=(self.jira_username, self.jira_api_token),
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "status": "success",
                        "message": "Conexão com JIRA estabelecida com sucesso",
                        "user": user_data.get("displayName", "Usuário"),
                        "account_id": user_data.get("accountId", "")
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Erro na conexão: {response.status_code}",
                        "details": response.text
                    }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao conectar com JIRA: {str(e)}"
            }

    async def _get_user_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Obtém informações de um usuário"""
        username = args.get("username", "")
        
        try:
            async with httpx.AsyncClient() as client:
                # Buscar usuário
                response = await client.get(
                    f"{self.jira_url}/rest/api/3/user/search",
                    params={"query": username},
                    auth=(self.jira_username, self.jira_api_token),
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    users = response.json()
                    if users:
                        user = users[0]
                        return {
                            "status": "success",
                            "user": {
                                "accountId": user.get("accountId", ""),
                                "displayName": user.get("displayName", ""),
                                "emailAddress": user.get("emailAddress", ""),
                                "active": user.get("active", False)
                            }
                        }
                    else:
                        return {
                            "status": "not_found",
                            "message": f"Usuário '{username}' não encontrado"
                        }
                else:
                    return {
                        "status": "error",
                        "message": f"Erro na busca: {response.status_code}",
                        "details": response.text
                    }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao buscar usuário: {str(e)}"
            }
    
    async def _create_test_issue(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um issue real no JIRA usando a API"""
        summary = args.get("summary", "")
        description = args.get("description", "Issue criado via MCP JIRA Admin")
        
        try:
            from datetime import datetime
            import base64
            
            # Verificar se as credenciais estão configuradas
            if not all([self.jira_url, self.jira_username, self.jira_api_token]):
                return {
                    "status": "error",
                    "message": "❌ Credenciais do JIRA não configuradas. Configure JIRA_URL, JIRA_USERNAME e JIRA_API_TOKEN no arquivo .env"
                }
            
            # Preparar autenticação
            auth_string = f"{self.jira_username}:{self.jira_api_token}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Primeiro, tentar acessar diretamente o projeto SCRUM conhecido
            async with httpx.AsyncClient() as client:
                # Primeiro, tentar acessar o projeto SCRUM diretamente
                logger.info("Tentando acessar projeto SCRUM diretamente...")
                scrum_response = await client.get(
                    f"{self.jira_url}/rest/api/3/project/SCRUM",
                    headers=headers,
                    timeout=30.0
                )
                
                if scrum_response.status_code == 200:
                    scrum_project = scrum_response.json()
                    logger.info(f"✅ Projeto SCRUM encontrado: {scrum_project.get('name')}")
                    projects = [scrum_project]
                else:
                    logger.info(f"Projeto SCRUM não acessível diretamente (status: {scrum_response.status_code})")
                    
                    # Buscar projetos disponíveis de forma genérica
                    projects_response = await client.get(
                        f"{self.jira_url}/rest/api/3/project",
                        headers=headers,
                        timeout=30.0
                    )
                    
                    if projects_response.status_code != 200:
                        return {
                            "status": "error",
                            "message": f"❌ Erro ao conectar com JIRA: {projects_response.status_code} - {projects_response.text}"
                        }
                    
                    projects = projects_response.json()
                    
                    # Debug: mostrar informações sobre projetos
                    logger.info(f"Projetos encontrados: {len(projects)}")
                    if projects:
                        for project in projects[:3]:  # Log primeiros 3 projetos
                            logger.info(f"Projeto: {project.get('key')} - {project.get('name')}")
                    
                    if not projects:
                        # Tentar buscar projetos com permissões diferentes
                        search_response = await client.get(
                            f"{self.jira_url}/rest/api/3/project/search",
                            headers=headers,
                            timeout=30.0
                        )
                        
                        if search_response.status_code == 200:
                            search_projects = search_response.json()
                            if search_projects.get('values'):
                                projects = search_projects['values']
                                logger.info(f"Projetos encontrados via search: {len(projects)}")
                        
                        if not projects:
                            return {
                                "status": "error",
                                "message": "❌ Nenhum projeto encontrado no JIRA. Verifique as permissões do usuário ou se há projetos disponíveis."
                            }
                
                # Usar o primeiro projeto disponível
                project_key = projects[0]["key"]
                project_name = projects[0]["name"]
                
                # Buscar tipos de issue disponíveis para o projeto
                issue_types_response = await client.get(
                    f"{self.jira_url}/rest/api/3/issuetype/project?projectId={projects[0]['id']}",
                    headers=headers,
                    timeout=30.0
                )
                
                if issue_types_response.status_code != 200:
                    # Fallback para tipos de issue gerais
                    issue_type_id = "10001"  # Task padrão
                    issue_type_name = "Task"
                else:
                    issue_types = issue_types_response.json()
                    # Procurar por Task, Story ou Bug
                    issue_type = next(
                        (it for it in issue_types if it["name"].lower() in ["task", "story", "bug"]),
                        issue_types[0] if issue_types else None
                    )
                    
                    if not issue_type:
                        return {
                            "status": "error",
                            "message": "❌ Nenhum tipo de issue disponível no projeto."
                        }
                    
                    issue_type_id = issue_type["id"]
                    issue_type_name = issue_type["name"]
                
                # Criar o issue
                issue_data = {
                    "fields": {
                        "project": {
                            "key": project_key
                        },
                        "summary": summary,
                        "description": {
                            "type": "doc",
                            "version": 1,
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": description
                                        }
                                    ]
                                }
                            ]
                        },
                        "issuetype": {
                            "id": issue_type_id
                        }
                    }
                }
                
                create_response = await client.post(
                    f"{self.jira_url}/rest/api/3/issue",
                    headers=headers,
                    json=issue_data,
                    timeout=30.0
                )
                
                if create_response.status_code not in [200, 201]:
                    error_detail = create_response.text
                    return {
                        "status": "error",
                        "message": f"❌ Erro ao criar issue: {create_response.status_code} - {error_detail}"
                    }
                
                created_issue = create_response.json()
                issue_key = created_issue["key"]
                issue_url = f"{self.jira_url}/browse/{issue_key}"
                
                # Registrar no log local
                log_file = "c:\\Users\\ebine\\OneDrive\\Documents\\MCP-Jira\\test_actions.json"
                
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        actions = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    actions = []
                
                action_log = {
                    "timestamp": datetime.now().isoformat(),
                    "action": "create_real_issue",
                    "data": {
                        "key": issue_key,
                        "summary": summary,
                        "description": description,
                        "project": project_name,
                        "project_key": project_key,
                        "issue_type": issue_type_name,
                        "url": issue_url,
                        "created": datetime.now().isoformat()
                    },
                    "success": True
                }
                
                actions.append(action_log)
                
                with open(log_file, 'w', encoding='utf-8') as f:
                    json.dump(actions, f, indent=2, ensure_ascii=False)
                
                return {
                    "status": "success",
                    "message": f"✅ Issue criado com sucesso no JIRA!",
                    "issue": {
                        "key": issue_key,
                        "summary": summary,
                        "project": project_name,
                        "project_key": project_key,
                        "issue_type": issue_type_name,
                        "url": issue_url
                    },
                    "log_file": log_file
                }
                
        except httpx.TimeoutException:
            return {
                "status": "error",
                "message": "❌ Timeout ao conectar com o JIRA. Verifique a URL e conexão de rede."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Erro inesperado: {str(e)}"
            }

    async def run(self):
        """Executa o servidor MCP"""
        logger.info("Iniciando servidor MCP JIRA Admin...")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    """Função principal"""
    try:
        server = SimpleJiraMCP()
        await server.run()
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())