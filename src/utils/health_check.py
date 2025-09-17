"""
Health Check Utility para MCP Admin Server
Implementa endpoint de saúde e verificações de conectividade
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any
from urllib.parse import urljoin

import httpx
from aiohttp import web

logger = logging.getLogger(__name__)

class HealthChecker:
    """Classe para verificações de saúde do sistema"""
    
    def __init__(self):
        self.jira_url = os.getenv("JIRA_URL")
        self.jira_username = os.getenv("JIRA_USERNAME")
        self.jira_api_token = os.getenv("JIRA_API_TOKEN")
        self.org_id = os.getenv("ORG_ID")
        self.admin_api_key = os.getenv("ADMIN_API_KEY")
    
    async def check_jira_connectivity(self) -> Dict[str, Any]:
        """Verificar conectividade com JIRA"""
        try:
            url = urljoin(self.jira_url, "/rest/api/3/myself")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url,
                    auth=(self.jira_username, self.jira_api_token)
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "status": "healthy",
                        "message": f"Conectado como {user_data.get('displayName', 'Unknown')}",
                        "user": user_data.get("accountId")
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "message": f"Erro HTTP {response.status_code}",
                        "error": response.text
                    }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": "Erro de conectividade com JIRA",
                "error": str(e)
            }
    
    async def check_org_api_connectivity(self) -> Dict[str, Any]:
        """Verificar conectividade com Organizations API"""
        try:
            url = f"https://api.atlassian.com/admin/v1/orgs/{self.org_id}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {self.admin_api_key}"}
                )
                
                if response.status_code == 200:
                    org_data = response.json()
                    return {
                        "status": "healthy",
                        "message": f"Conectado à organização {org_data.get('name', 'Unknown')}",
                        "org_id": self.org_id
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "message": f"Erro HTTP {response.status_code}",
                        "error": response.text
                    }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": "Erro de conectividade com Organizations API",
                "error": str(e)
            }
    
    async def check_environment_variables(self) -> Dict[str, Any]:
        """Verificar variáveis de ambiente obrigatórias"""
        required_vars = [
            "JIRA_URL", "JIRA_USERNAME", "JIRA_API_TOKEN",
            "ORG_ID", "ADMIN_API_KEY"
        ]
        
        missing_vars = []
        configured_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if value:
                configured_vars.append(var)
            else:
                missing_vars.append(var)
        
        if missing_vars:
            return {
                "status": "unhealthy",
                "message": f"Variáveis de ambiente não configuradas: {', '.join(missing_vars)}",
                "configured": configured_vars,
                "missing": missing_vars
            }
        else:
            return {
                "status": "healthy",
                "message": "Todas as variáveis de ambiente estão configuradas",
                "configured": configured_vars
            }
    
    async def get_full_health_status(self) -> Dict[str, Any]:
        """Obter status completo de saúde do sistema"""
        checks = {
            "environment": await self.check_environment_variables(),
            "jira_connectivity": await self.check_jira_connectivity(),
            "org_api_connectivity": await self.check_org_api_connectivity()
        }
        
        # Determinar status geral
        all_healthy = all(check["status"] == "healthy" for check in checks.values())
        overall_status = "healthy" if all_healthy else "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": asyncio.get_event_loop().time(),
            "checks": checks,
            "version": "1.0.0",
            "port": int(os.getenv("MCP_PORT", 6000))
        }

# Handler para endpoint HTTP de health check
async def health_endpoint(request):
    """Endpoint HTTP para verificação de saúde"""
    health_checker = HealthChecker()
    health_status = await health_checker.get_full_health_status()
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return web.json_response(
        health_status,
        status=status_code,
        headers={"Content-Type": "application/json"}
    )

# Função para criar aplicação web simples com health check
def create_health_app():
    """Criar aplicação web para health check"""
    app = web.Application()
    app.router.add_get('/health', health_endpoint)
    app.router.add_get('/', health_endpoint)  # Root também retorna health
    
    return app

async def run_health_server(port: int = 6000):
    """Executar servidor de health check"""
    app = create_health_app()
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"Health check server rodando na porta {port}")
    
    # Manter servidor rodando
    try:
        while True:
            await asyncio.sleep(3600)  # Sleep por 1 hora
    except KeyboardInterrupt:
        logger.info("Parando health check server...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    # Executar apenas o health check server para testes
    asyncio.run(run_health_server())