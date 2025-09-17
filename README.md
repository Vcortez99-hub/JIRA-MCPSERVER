# MCP-JIRA Integration

Este projeto configura a integração entre JIRA e MCP (Model Context Protocol) com duas abordagens:

1. **MCP Oficial da Atlassian** - Para operações básicas (buscar issues, criar issues, etc.)
2. **MCP Admin Personalizado** - Para operações administrativas (criar usuários, gerenciar permissões, etc.)

## Estrutura do Projeto

```
MCP-Jira/
├── config/
│   ├── claude_desktop_config.json    # Configuração para Claude Desktop
│   ├── mcp_config.json              # Configuração genérica MCP
│   └── environment.example.env       # Exemplo de variáveis de ambiente
├── docker/
│   ├── Dockerfile                   # Container para MCP Admin
│   ├── docker-compose.yml           # Orquestração dos serviços
│   └── requirements.txt             # Dependências Python
├── src/
│   ├── mcp_admin_server.py          # Servidor MCP para operações admin
│   ├── tools/                       # Ferramentas MCP personalizadas
│   └── utils/                       # Utilitários e helpers
├── scripts/
│   ├── setup.ps1                    # Script de configuração inicial
│   ├── start_services.ps1           # Iniciar serviços
│   └── stop_services.ps1            # Parar serviços
└── docs/
    ├── setup_guide.md               # Guia de configuração
    └── api_reference.md             # Referência das APIs
```

## Pré-requisitos

- Node.js (para MCP oficial)
- Docker Desktop (para MCP admin)
- PowerShell (para scripts de automação)
- Credenciais JIRA:
  - URL da instância JIRA
  - Email do usuário
  - API Token
  - Admin API Key (para operações administrativas)
  - Organization ID

## Configuração Rápida

1. Execute o script de setup:
   ```powershell
   .\scripts\setup.ps1
   ```

2. Configure suas credenciais no arquivo `.env`

3. Inicie os serviços:
   ```powershell
   .\scripts\start_services.ps1
   ```

## Porta Padrão

O servidor MCP admin roda na **porta 6000** conforme solicitado.