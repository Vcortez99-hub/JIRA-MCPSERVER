#!/usr/bin/env python3
"""
Script de teste para o MCP JIRA Server
Testa a criação real de issues no JIRA usando as credenciais do .env
"""

import asyncio
import json
from src.simple_mcp_server import SimpleJiraMCP

async def test_real_jira_creation():
    """Testa a criação real de issues no JIRA"""
    print("🚀 Iniciando teste de criação real de issues no JIRA...")
    
    # Criar instância do servidor
    server = SimpleJiraMCP()
    
    # Teste 1: Criar issue de teste
    print("\n📝 Teste 1: Criando issue de teste...")
    result1 = await server._create_test_issue({
        "summary": "Issue de Teste - MCP JIRA Admin",
        "description": "Este é um issue criado automaticamente pelo MCP JIRA Admin para testar a integração com o JIRA real."
    })
    
    print(f"Resultado: {result1['message']}")
    if result1['status'] == 'success':
        issue = result1['issue']
        print(f"✅ Issue criado: {issue['key']} - {issue['summary']}")
        print(f"🔗 URL: {issue['url']}")
        print(f"📁 Projeto: {issue['project']} ({issue['project_key']})")
        print(f"🏷️ Tipo: {issue['issue_type']}")
    else:
        print(f"❌ Erro: {result1['message']}")
        return
    
    # Teste 2: Criar outro issue com descrição diferente
    print("\n📝 Teste 2: Criando segundo issue...")
    result2 = await server._create_test_issue({
        "summary": "Bug Report - Teste de Integração",
        "description": "Issue criado para demonstrar a funcionalidade de criação automática de tickets via MCP. Este é um exemplo de bug report."
    })
    
    print(f"Resultado: {result2['message']}")
    if result2['status'] == 'success':
        issue = result2['issue']
        print(f"✅ Issue criado: {issue['key']} - {issue['summary']}")
        print(f"🔗 URL: {issue['url']}")
        print(f"📁 Projeto: {issue['project']} ({issue['project_key']})")
        print(f"🏷️ Tipo: {issue['issue_type']}")
    else:
        print(f"❌ Erro: {result2['message']}")
    
    # Verificar arquivo de log
    print("\n📊 Verificando arquivo de log...")
    try:
        with open("test_actions.json", "r", encoding="utf-8") as f:
            actions = json.load(f)
        
        real_issues = [action for action in actions if action.get("action") == "create_real_issue"]
        print(f"✅ Total de issues reais criados: {len(real_issues)}")
        
        for i, action in enumerate(real_issues[-2:], 1):  # Mostrar os 2 últimos
            data = action["data"]
            print(f"  {i}. {data['key']}: {data['summary']}")
            print(f"     🔗 {data['url']}")
            
    except FileNotFoundError:
        print("❌ Arquivo de log não encontrado")
    except json.JSONDecodeError:
        print("❌ Erro ao ler arquivo de log")
    
    print("\n🎉 Teste concluído!")
    print("\n📋 Próximos passos:")
    print("1. Verifique os issues criados no seu JIRA")
    print("2. Acesse as URLs mostradas acima")
    print("3. Visualize o frontend em: file:///c:/Users/ebine/OneDrive/Documents/MCP-Jira/frontend/index.html")

if __name__ == "__main__":
    asyncio.run(test_real_jira_creation())