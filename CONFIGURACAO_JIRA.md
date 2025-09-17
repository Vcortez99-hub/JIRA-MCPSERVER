# 🔧 Configuração do JIRA para MCP JIRA Admin

## 📋 Pré-requisitos

Para usar o MCP JIRA Admin com seu JIRA real, você precisa configurar as credenciais no arquivo `.env`.

## 🔑 Obtendo as Credenciais do JIRA

### 1. URL do JIRA
- Sua URL do JIRA Cloud: `https://sua-empresa.atlassian.net`
- Exemplo: `https://minhaempresa.atlassian.net`

### 2. Username (Email)
- Use o email da sua conta Atlassian
- Exemplo: `joao.silva@minhaempresa.com`

### 3. API Token
Para criar um API Token:

1. **Acesse**: https://id.atlassian.com/manage-profile/security/api-tokens
2. **Clique em**: "Create API token"
3. **Digite um nome**: "MCP JIRA Admin"
4. **Copie o token**: Guarde em local seguro (só aparece uma vez)

## ⚙️ Configurando o Arquivo .env

1. **Abra o arquivo**: `docker/.env`
2. **Substitua os valores placeholder**:

```env
# Configurações do JIRA
JIRA_URL=https://sua-empresa.atlassian.net
JIRA_USERNAME=seu-email@empresa.com
JIRA_API_TOKEN=seu-token-aqui
ORG_ID=sua-org-id

# Configurações do servidor MCP
MCP_HOST=0.0.0.0
MCP_PORT=6000

# Configuração opcional do Admin API
ADMIN_API_KEY=admin-key-123
```

### Exemplo Preenchido:
```env
# Configurações do JIRA
JIRA_URL=https://minhaempresa.atlassian.net
JIRA_USERNAME=joao.silva@minhaempresa.com
JIRA_API_TOKEN=ATATT3xFfGF0T4JVjdmjXKZvBhUKEHfxw9RrOof5TjNvBhUKEHfxw9RrOof5TjNv
ORG_ID=12345

# Configurações do servidor MCP
MCP_HOST=0.0.0.0
MCP_PORT=6000

# Configuração opcional do Admin API
ADMIN_API_KEY=admin-key-123
```

## 🧪 Testando a Configuração

Após configurar as credenciais, execute o teste:

```bash
python test_mcp.py
```

### ✅ Resultado Esperado:
```
🚀 Iniciando teste de criação real de issues no JIRA...

📝 Teste 1: Criando issue de teste...
Resultado: ✅ Issue criado com sucesso no JIRA!
✅ Issue criado: PROJ-123 - Issue de Teste - MCP JIRA Admin
🔗 URL: https://minhaempresa.atlassian.net/browse/PROJ-123
📁 Projeto: Meu Projeto (PROJ)
🏷️ Tipo: Task

📝 Teste 2: Criando segundo issue...
Resultado: ✅ Issue criado com sucesso no JIRA!
✅ Issue criado: PROJ-124 - Bug Report - Teste de Integração
🔗 URL: https://minhaempresa.atlassian.net/browse/PROJ-124
📁 Projeto: Meu Projeto (PROJ)
🏷️ Tipo: Task

📊 Verificando arquivo de log...
✅ Total de issues reais criados: 2
  1. PROJ-123: Issue de Teste - MCP JIRA Admin
     🔗 https://minhaempresa.atlassian.net/browse/PROJ-123
  2. PROJ-124: Bug Report - Teste de Integração
     🔗 https://minhaempresa.atlassian.net/browse/PROJ-124

🎉 Teste concluído!

📋 Próximos passos:
1. Verifique os issues criados no seu JIRA
2. Acesse as URLs mostradas acima
3. Visualize o frontend em: file:///c:/Users/ebine/OneDrive/Documents/MCP-Jira/frontend/index.html
```

## 🚨 Possíveis Erros

### ❌ "Credenciais do JIRA não configuradas"
- **Causa**: Arquivo `.env` não configurado
- **Solução**: Configure as credenciais conforme instruções acima

### ❌ "Erro ao conectar com JIRA: 401"
- **Causa**: Credenciais inválidas
- **Solução**: Verifique email e API token

### ❌ "Erro ao conectar com JIRA: 403"
- **Causa**: Sem permissão para criar issues
- **Solução**: Verifique permissões no projeto JIRA

### ❌ "Nenhum projeto encontrado no JIRA"
- **Causa**: Usuário sem acesso a projetos
- **Solução**: Solicite acesso ao administrador do JIRA

## 🔒 Segurança

- ⚠️ **NUNCA** compartilhe seu API Token
- ⚠️ **NÃO** commite o arquivo `.env` no Git
- ✅ Use tokens com permissões mínimas necessárias
- ✅ Revogue tokens não utilizados

## 📞 Suporte

Se encontrar problemas:
1. Verifique as credenciais no arquivo `.env`
2. Teste a conexão com o JIRA manualmente
3. Verifique as permissões do usuário no projeto
4. Consulte os logs de erro detalhados