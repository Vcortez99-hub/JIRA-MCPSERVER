#!/usr/bin/env python3
"""
Script para adicionar comentário no card SCRUM-40
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def add_comment_to_issue():
    """Adiciona comentário ao issue SCRUM-40"""
    
    # Configurações do JIRA (valores diretos para teste)
    jira_url = "https://canalrural-devskin.atlassian.net"
    username = "viniciuscortez03@gmail.com"
    token = os.getenv("JIRA_API_TOKEN", "YOUR_API_TOKEN_HERE")
    
    print("🎯 ADICIONANDO COMENTÁRIO NO SCRUM-40")
    print("=" * 50)
    print(f"URL: {jira_url}")
    print(f"Username: {username}")
    
    # Issue key
    issue_key = "SCRUM-40"
    
    # Comentário a ser adicionado
    comment_text = "Teste Integração"
    
    # URL da API para adicionar comentário
    url = f"{jira_url}/rest/api/3/issue/{issue_key}/comment"
    
    # Headers
    import base64
    auth_string = base64.b64encode(f'{username}:{token}'.encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_string}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Payload do comentário
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": comment_text
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        print(f"\n1️⃣ Adicionando comentário no {issue_key}...")
        print(f"   Comentário: {comment_text}")
        
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            comment_data = response.json()
            print(f"   ✅ COMENTÁRIO ADICIONADO COM SUCESSO!")
            print(f"   ID do Comentário: {comment_data.get('id')}")
            print(f"   Autor: {comment_data.get('author', {}).get('displayName')}")
            print(f"   Criado em: {comment_data.get('created')}")
            
            # Salvar informações da ação
            action_info = {
                "timestamp": datetime.now().isoformat(),
                "action": "add_comment",
                "success": True,
                "data": {
                    "issue_key": issue_key,
                    "comment": comment_text,
                    "comment_id": comment_data.get('id'),
                    "author": comment_data.get('author', {}).get('displayName'),
                    "created": comment_data.get('created')
                }
            }
            
            # Atualizar arquivo de ações
            update_actions_file(action_info)
            
            return True
            
        else:
            print(f"   ❌ Erro ao adicionar comentário: {response.text}")
            
            # Salvar erro
            action_info = {
                "timestamp": datetime.now().isoformat(),
                "action": "add_comment",
                "success": False,
                "error": response.text,
                "data": {
                    "issue_key": issue_key,
                    "comment": comment_text
                }
            }
            
            update_actions_file(action_info)
            return False
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {str(e)}")
        
        # Salvar erro
        action_info = {
            "timestamp": datetime.now().isoformat(),
            "action": "add_comment",
            "success": False,
            "error": str(e),
            "data": {
                "issue_key": issue_key,
                "comment": comment_text
            }
        }
        
        update_actions_file(action_info)
        return False

def update_actions_file(new_action):
    """Atualiza o arquivo de ações com a nova ação"""
    
    actions_file = "test_actions.json"
    frontend_actions_file = "frontend/test_actions.json"
    
    try:
        # Ler ações existentes
        if os.path.exists(actions_file):
            with open(actions_file, 'r', encoding='utf-8') as f:
                actions = json.load(f)
        else:
            actions = []
        
        # Adicionar nova ação no início da lista
        actions.insert(0, new_action)
        
        # Salvar no arquivo principal
        with open(actions_file, 'w', encoding='utf-8') as f:
            json.dump(actions, f, indent=4, ensure_ascii=False)
        
        # Salvar também na pasta frontend
        with open(frontend_actions_file, 'w', encoding='utf-8') as f:
            json.dump(actions, f, indent=4, ensure_ascii=False)
        
        print(f"   📄 Ações atualizadas em: {actions_file} e {frontend_actions_file}")
        
    except Exception as e:
        print(f"   ⚠️ Erro ao atualizar arquivo de ações: {str(e)}")

if __name__ == "__main__":
    success = add_comment_to_issue()
    if success:
        print("\n🎉 Comentário adicionado com sucesso!")
    else:
        print("\n❌ Falha ao adicionar comentário.")