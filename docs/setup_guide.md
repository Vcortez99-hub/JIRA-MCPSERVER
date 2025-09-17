# Guia de Configuração MCP-JIRA

Este guia detalha como configurar e usar a integração entre JIRA e MCP (Model Context Protocol).

## Visão Geral

A integração MCP-JIRA oferece duas abordagens complementares:

1. **MCP Oficial da Atlassian** - Para operações básicas do dia a dia
2. **MCP Admin Personalizado** - Para operações administrativas avançadas

## Pré-requisitos

### Software Necessário

- **Node.js** (versão 16 ou superior)
- **Docker Desktop** (para o servidor admin)
- **PowerShell** (para scripts de automação)
- **Cliente MCP** (Claude Desktop, VS Code, Cursor, etc.)

### Credenciais JIRA

Você precisará das seguintes credenciais:

#### Para Operações Básicas
- **JIRA_URL**: URL da sua instância JIRA (ex: `https://sua-org.atlassian.net`)
- **JIRA_USERNAME**: Seu email de usuário
- **JIRA_API_TOKEN**: Token de API do JIRA

#### Para Operações Administrativas
- **ORG_ID**: ID da sua organização Atlassian
- **ADMIN_API_KEY**: Chave de API de administrador

### Como Obter as Credenciais

#### 1. JIRA API Token
1. Acesse [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Clique em "Create API token"
3. Dê um nome descritivo (ex: "MCP Integration")
4. Copie o token gerado

#### 2. Admin API Key e Organization ID
1. Acesse [admin.atlassian.com](https://admin.atlassian.com)
2. Vá em **Settings** → **API keys**
3. Clique em "Create API key"
4. Configure os escopos necessários:
   - User management
   - Group management
   - Organization management
5. Copie a chave gerada
6. O Organization ID está visível na URL ou nas configurações da organização

## Configuração Passo a Passo

### 1. Configuração Inicial

```powershell
# Clone ou baixe o projeto
cd "c:\Users\ebine\OneDrive\Documents\MCP-Jira"

# Execute o script de setup
.\scripts\setup.ps1
```

### 2. Configurar Credenciais

1. Copie o arquivo de exemplo:
   ```powershell
   Copy-Item config\environment.example.env .env
   ```

2. Edite o arquivo `.env` com suas credenciais:
   ```env
   JIRA_URL=https://sua-org.atlassian.net
   JIRA_USERNAME=seu.email@suaorg.com
   JIRA_API_TOKEN=seu_token_aqui
   ORG_ID=sua_org_id
   ADMIN_API_KEY=sua_admin_key
   ```

### 3. Iniciar Serviços

```powershell
# Inicia o servidor MCP Admin
.\scripts\start_services.ps1
```

### 4. Configurar MCP Oficial

Execute o comando para conectar ao MCP oficial:

```bash
npx -y mcp-remote https://mcp.atlassian.com/v1/sse
```

Complete o login OAuth no browser quando solicitado.

### 5. Configurar Cliente MCP

#### Para Claude Desktop

Copie o conteúdo de `config\claude_desktop_config.json` para seu arquivo de configuração do Claude Desktop (geralmente em `%APPDATA%\Claude\claude_desktop_config.json`).

#### Para VS Code/Cursor

Use a configuração em `config\mcp_config.json` como referência para configurar a extensão MCP.

## Uso

### Operações Básicas (MCP Oficial)

```
"Busque todas as issues do projeto PROJ com status Aberto"
"Crie uma issue 'Implementar SSO' no projeto PROJ e atribua ao @fulano"
"Crie uma página no Confluence sobre o novo processo"
```

### Operações Administrativas (MCP Admin)

```
"Crie o usuário maria@empresa.com sem produto por enquanto"
"Adicione maria@empresa.com aos grupos jira-software-users e finance"
"Coloque maria@empresa.com no papel 'Developers' do projeto FIN"
"No permission scheme 12345, conceda 'BROWSE_PROJECTS' ao grupo auditors"
```

## Ferramentas Disponíveis

### MCP Oficial da Atlassian

- `search_issues` - Buscar issues
- `create_issue` - Criar nova issue
- `update_issue` - Atualizar issue existente
- `create_page` - Criar página no Confluence
- `search_pages` - Buscar páginas

### MCP Admin Personalizado

- `create_user` - Criar novo usuário
- `add_user_to_group` - Adicionar usuário a grupo
- `assign_project_role` - Atribuir papel de projeto
- `grant_permission` - Conceder permissão em esquema
- `list_project_roles` - Listar papéis de projeto
- `list_permission_schemes` - Listar esquemas de permissões

## Solução de Problemas

### Servidor MCP Admin não inicia

1. Verifique se o Docker está rodando:
   ```powershell
   docker info
   ```

2. Verifique as variáveis de ambiente:
   ```powershell
   Get-Content .env
   ```

3. Verifique os logs do container:
   ```powershell
   docker logs mcp-jira-admin
   ```

### Erro de autenticação

1. Verifique se o API token está correto
2. Confirme se o usuário tem as permissões necessárias
3. Teste a conexão manualmente:
   ```powershell
   curl -u "email:token" "https://sua-org.atlassian.net/rest/api/3/myself"
   ```

### MCP Oficial não conecta

1. Verifique sua conexão com a internet
2. Tente executar novamente o comando OAuth:
   ```bash
   npx -y mcp-remote https://mcp.atlassian.com/v1/sse
   ```
3. Limpe o cache do npm se necessário:
   ```bash
   npm cache clean --force
   ```

## Segurança

### Boas Práticas

1. **Nunca commite credenciais** no controle de versão
2. **Use tokens com expiração** apropriada
3. **Revogue tokens** não utilizados regularmente
4. **Aplique princípio do menor privilégio**
5. **Monitore logs** de acesso e uso

### Permissões Necessárias

#### Para JIRA API Token
- **Administer Jira** (global) - para operações de usuário e permissões
- **Browse Projects** - para listar projetos
- **Administer Projects** - para gerenciar papéis de projeto

#### Para Admin API Key
- **Organization Admin** - para gerenciar usuários e grupos
- **User Management** - para operações de provisionamento

## Manutenção

### Atualizar Dependências

```powershell
# Atualizar MCP oficial
npx -y mcp-remote@latest https://mcp.atlassian.com/v1/sse

# Reconstruir imagem Docker
docker-compose build --no-cache
```

### Backup de Configurações

Faça backup regular dos arquivos:
- `.env` (sem commitar no git)
- `config/claude_desktop_config.json`
- `config/mcp_config.json`

### Logs e Monitoramento

```powershell
# Ver logs do servidor admin
docker logs -f mcp-jira-admin

# Verificar status dos serviços
docker-compose ps

# Verificar saúde do servidor
curl http://localhost:6000/health
```

## Suporte

Para problemas ou dúvidas:

1. Verifique os logs de erro
2. Consulte a documentação oficial da Atlassian
3. Teste as APIs manualmente para isolar problemas
4. Verifique as permissões do usuário no JIRA

## Referências

- [Atlassian REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Organizations API](https://developer.atlassian.com/cloud/admin/organization/)
- [User Management API](https://developer.atlassian.com/cloud/admin/user-management/)