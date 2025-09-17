#!/usr/bin/env python3
"""
MCP Admin Server para JIRA
Servidor MCP personalizado para operações administrativas do JIRA
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JiraAdminMCP:
    def __init__(self):
        self.jira_url = os.getenv("JIRA_URL")
        self.jira_username = os.getenv("JIRA_USERNAME")
        self.jira_api_token = os.getenv("JIRA_API_TOKEN")
        self.org_id = os.getenv("ORG_ID")
        self.admin_api_key = os.getenv("ADMIN_API_KEY")
        self.port = int(os.getenv("MCP_PORT", 6000))
        
        # Verificar variáveis obrigatórias (exceto ADMIN_API_KEY que é opcional)
        required_vars = ['JIRA_URL', 'JIRA_USERNAME', 'JIRA_API_TOKEN', 'ORG_ID']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Variáveis de ambiente obrigatórias não configuradas: {missing_vars}")
            raise ValueError(f"Variáveis de ambiente obrigatórias não configuradas: {missing_vars}")
        
        self.server = Server("jira-admin-mcp")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura os handlers do servidor MCP"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """Lista todas as ferramentas disponíveis"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="create_user",
                        description="Criar novo usuário no JIRA",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "email": {"type": "string", "description": "Email do usuário"},
                                "display_name": {"type": "string", "description": "Nome de exibição"},
                                "products": {"type": "array", "items": {"type": "string"}, "description": "Produtos para dar acesso"}
                            },
                            "required": ["email"]
                        }
                    ),
                    Tool(
                        name="add_user_to_group",
                        description="Adicionar usuário a um grupo",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "account_id": {"type": "string", "description": "ID da conta do usuário"},
                                "group_name": {"type": "string", "description": "Nome do grupo"}
                            },
                            "required": ["account_id", "group_name"]
                        }
                    ),
                    Tool(
                        name="assign_project_role",
                        description="Atribuir usuário a papel do projeto",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "project_key": {"type": "string", "description": "Chave do projeto"},
                                "role_id": {"type": "string", "description": "ID do papel"},
                                "account_id": {"type": "string", "description": "ID da conta do usuário"},
                                "group_name": {"type": "string", "description": "Nome do grupo (alternativo ao account_id)"}
                            },
                            "required": ["project_key", "role_id"]
                        }
                    ),
                    Tool(
                        name="grant_permission",
                        description="Conceder permissão em esquema de permissões",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "scheme_id": {"type": "string", "description": "ID do esquema de permissões"},
                                "permission": {"type": "string", "description": "Nome da permissão"},
                                "holder_type": {"type": "string", "enum": ["group", "user"], "description": "Tipo do detentor"},
                                "holder_parameter": {"type": "string", "description": "Parâmetro do detentor (nome do grupo ou account_id)"}
                            },
                            "required": ["scheme_id", "permission", "holder_type", "holder_parameter"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Executa uma ferramenta específica"""
            try:
                if name == "create_user":
                    result = await self._create_user(arguments)
                elif name == "add_user_to_group":
                    result = await self._add_user_to_group(arguments)
                elif name == "assign_project_role":
                    result = await self._assign_project_role(arguments)
                elif name == "grant_permission":
                    result = await self._grant_permission(arguments)
                else:
                    raise ValueError(f"Ferramenta desconhecida: {name}")
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                )
            except Exception as e:
                logger.error(f"Erro ao executar ferramenta {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Erro: {str(e)}")]
                )
    
    async def _create_user(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Criar novo usuário no JIRA"""
        url = urljoin(self.jira_url, "/rest/api/3/user")
        
        payload = {
            "emailAddress": args["email"],
            "products": args.get("products", [])
        }
        
        if "display_name" in args:
            payload["displayName"] = args["display_name"]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                auth=(self.jira_username, self.jira_api_token),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
    
    async def _add_user_to_group(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Adicionar usuário a grupo via Organizations API"""
        # Esta implementação usa a Organizations API da Atlassian
        url = f"https://api.atlassian.com/admin/v1/orgs/{self.org_id}/users/{args['account_id']}/manage/groups"
        
        payload = {
            "groupIds": [args["group_name"]]  # Assumindo que group_name é o ID do grupo
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.admin_api_key}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            return {"status": "success", "message": f"Usuário adicionado ao grupo {args['group_name']}"}
    
    async def _assign_project_role(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Atribuir usuário/grupo a papel do projeto"""
        url = urljoin(self.jira_url, f"/rest/api/3/project/{args['project_key']}/role/{args['role_id']}")
        
        categorised_actors = {}
        
        if "account_id" in args:
            categorised_actors["atlassian-user-role-actor"] = [args["account_id"]]
        
        if "group_name" in args:
            categorised_actors["atlassian-group-role-actor"] = [args["group_name"]]
        
        payload = {"categorisedActors": categorised_actors}
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                json=payload,
                auth=(self.jira_username, self.jira_api_token),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
    
    async def _grant_permission(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Conceder permissão em esquema de permissões"""
        url = urljoin(self.jira_url, f"/rest/api/3/permissionscheme/{args['scheme_id']}/permission")
        
        payload = {
            "holder": {
                "type": args["holder_type"],
                "parameter": args["holder_parameter"]
            },
            "permission": args["permission"]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                auth=(self.jira_username, self.jira_api_token),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
    
    async def run(self):
        """Executar o servidor MCP"""
        logger.info(f"Iniciando servidor MCP Admin na porta {self.port}")
        
        # Para este exemplo, usamos stdio_server
        # Em produção, você pode querer usar um servidor HTTP
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="jira-admin-mcp",
                    server_version="1.0.0",
                ),
            )

async def main():
    """Função principal"""
    try:
        admin_server = JiraAdminMCP()
        await admin_server.run()
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())