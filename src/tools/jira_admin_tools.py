"""
Ferramentas MCP para Administração do JIRA
Implementa as principais operações administrativas do JIRA
"""

import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx

logger = logging.getLogger(__name__)

class JiraAdminTools:
    """Classe com ferramentas administrativas para JIRA"""
    
    def __init__(self, jira_url: str, username: str, api_token: str, 
                 org_id: str, admin_api_key: str):
        self.jira_url = jira_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.org_id = org_id
        self.admin_api_key = admin_api_key
        
        # URLs base para diferentes APIs
        self.jira_api_base = f"{self.jira_url}/rest/api/3"
        self.org_api_base = f"https://api.atlassian.com/admin/v1/orgs/{self.org_id}"
    
    async def create_user_invitation(self, email: str, display_name: Optional[str] = None, 
                                   products: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Criar convite para novo usuário no JIRA
        
        Args:
            email: Email do usuário
            display_name: Nome de exibição (opcional)
            products: Lista de produtos para dar acesso (opcional)
        
        Returns:
            Resposta da API com dados do usuário criado
        """
        url = f"{self.jira_api_base}/user"
        
        payload = {
            "emailAddress": email,
            "products": products or []
        }
        
        if display_name:
            payload["displayName"] = display_name
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                auth=(self.username, self.api_token),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                logger.info(f"Usuário {email} criado com sucesso")
                return response.json()
            else:
                error_msg = f"Erro ao criar usuário: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Buscar usuário por email
        
        Args:
            email: Email do usuário
        
        Returns:
            Dados do usuário ou None se não encontrado
        """
        url = f"{self.jira_api_base}/user/search"
        params = {"query": email}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                auth=(self.username, self.api_token)
            )
            
            if response.status_code == 200:
                users = response.json()
                for user in users:
                    if user.get("emailAddress", "").lower() == email.lower():
                        return user
                return None
            else:
                logger.error(f"Erro ao buscar usuário: {response.status_code}")
                return None
    
    async def add_user_to_group_org_api(self, account_id: str, group_id: str) -> Dict[str, Any]:
        """
        Adicionar usuário a grupo via Organizations API
        
        Args:
            account_id: ID da conta do usuário
            group_id: ID do grupo
        
        Returns:
            Resultado da operação
        """
        url = f"{self.org_api_base}/users/{account_id}/manage/groups"
        
        payload = {"groupIds": [group_id]}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.admin_api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code in [200, 204]:
                logger.info(f"Usuário {account_id} adicionado ao grupo {group_id}")
                return {"status": "success", "message": "Usuário adicionado ao grupo"}
            else:
                error_msg = f"Erro ao adicionar usuário ao grupo: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
    
    async def assign_project_role(self, project_key: str, role_id: str, 
                                account_ids: Optional[List[str]] = None,
                                group_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Atribuir usuários/grupos a papel do projeto
        
        Args:
            project_key: Chave do projeto
            role_id: ID do papel
            account_ids: Lista de IDs de contas de usuários (opcional)
            group_names: Lista de nomes de grupos (opcional)
        
        Returns:
            Resultado da operação
        """
        url = f"{self.jira_api_base}/project/{project_key}/role/{role_id}"
        
        categorised_actors = {}
        
        if account_ids:
            categorised_actors["atlassian-user-role-actor"] = account_ids
        
        if group_names:
            categorised_actors["atlassian-group-role-actor"] = group_names
        
        if not categorised_actors:
            raise ValueError("Deve fornecer pelo menos account_ids ou group_names")
        
        payload = {"categorisedActors": categorised_actors}
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                json=payload,
                auth=(self.username, self.api_token),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"Papel {role_id} atribuído no projeto {project_key}")
                return response.json()
            else:
                error_msg = f"Erro ao atribuir papel: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
    
    async def grant_permission_to_scheme(self, scheme_id: str, permission: str,
                                       holder_type: str, holder_parameter: str) -> Dict[str, Any]:
        """
        Conceder permissão em esquema de permissões
        
        Args:
            scheme_id: ID do esquema de permissões
            permission: Nome da permissão (ex: BROWSE_PROJECTS)
            holder_type: Tipo do detentor (group, user, etc.)
            holder_parameter: Parâmetro do detentor (nome do grupo, account_id, etc.)
        
        Returns:
            Resultado da operação
        """
        url = f"{self.jira_api_base}/permissionscheme/{scheme_id}/permission"
        
        payload = {
            "holder": {
                "type": holder_type,
                "parameter": holder_parameter
            },
            "permission": permission
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                auth=(self.username, self.api_token),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                logger.info(f"Permissão {permission} concedida no esquema {scheme_id}")
                return response.json()
            else:
                error_msg = f"Erro ao conceder permissão: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
    
    async def list_project_roles(self, project_key: str) -> Dict[str, Any]:
        """
        Listar papéis disponíveis em um projeto
        
        Args:
            project_key: Chave do projeto
        
        Returns:
            Lista de papéis do projeto
        """
        url = f"{self.jira_api_base}/project/{project_key}/role"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                auth=(self.username, self.api_token)
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Erro ao listar papéis: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
    
    async def list_permission_schemes(self) -> Dict[str, Any]:
        """
        Listar esquemas de permissões disponíveis
        
        Returns:
            Lista de esquemas de permissões
        """
        url = f"{self.jira_api_base}/permissionscheme"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                auth=(self.username, self.api_token)
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Erro ao listar esquemas: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
    
    async def get_groups_for_org(self) -> Dict[str, Any]:
        """
        Listar grupos da organização via Organizations API
        
        Returns:
            Lista de grupos da organização
        """
        url = f"{self.org_api_base}/groups"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {self.admin_api_key}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Erro ao listar grupos: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)