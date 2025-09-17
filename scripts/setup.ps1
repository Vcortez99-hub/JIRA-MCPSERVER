# MCP-JIRA Setup Script
# Este script configura o ambiente para integração JIRA-MCP

Write-Host "=== MCP-JIRA Setup ===" -ForegroundColor Green

# Verificar se Node.js está instalado
Write-Host "Verificando Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Node.js não encontrado. Instale Node.js antes de continuar." -ForegroundColor Red
    exit 1
}

# Verificar se Docker está instalado
Write-Host "Verificando Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "Docker encontrado: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Docker não encontrado. Instale Docker Desktop antes de continuar." -ForegroundColor Red
    exit 1
}

# Criar arquivo .env se não existir
if (-not (Test-Path ".env")) {
    Write-Host "Criando arquivo .env..." -ForegroundColor Yellow
    Copy-Item "config\environment.example.env" ".env"
    Write-Host "IMPORTANTE: Configure suas credenciais no arquivo .env antes de continuar!" -ForegroundColor Red
}

# Testar conexão com MCP oficial da Atlassian
Write-Host "Testando MCP oficial da Atlassian..." -ForegroundColor Yellow
Write-Host "Execute o comando abaixo para fazer login OAuth:" -ForegroundColor Cyan
Write-Host "npx -y mcp-remote https://mcp.atlassian.com/v1/sse" -ForegroundColor White

# Construir imagem Docker para MCP Admin
Write-Host "Construindo imagem Docker para MCP Admin..." -ForegroundColor Yellow
Set-Location docker
docker build -t mcp-jira-admin:latest .
if ($LASTEXITCODE -eq 0) {
    Write-Host "Imagem Docker construída com sucesso!" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha ao construir imagem Docker." -ForegroundColor Red
    exit 1
}
Set-Location ..

Write-Host "=== Setup Concluído ===" -ForegroundColor Green
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Configure suas credenciais no arquivo .env" -ForegroundColor White
Write-Host "2. Execute: .\scripts\start_services.ps1" -ForegroundColor White
Write-Host "3. Faça o login OAuth quando solicitado" -ForegroundColor White