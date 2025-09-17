# Script para iniciar os serviços MCP-JIRA
# Executa tanto o MCP oficial quanto o servidor admin local

Write-Host "=== Iniciando Serviços MCP-JIRA ===" -ForegroundColor Green

# Verificar se arquivo .env existe
if (-not (Test-Path ".env")) {
    Write-Host "ERRO: Arquivo .env não encontrado!" -ForegroundColor Red
    Write-Host "Copie o arquivo config\environment.example.env para .env e configure suas credenciais." -ForegroundColor Yellow
    exit 1
}

# Carregar variáveis de ambiente
Write-Host "Carregando variáveis de ambiente..." -ForegroundColor Yellow
Get-Content .env | ForEach-Object {
    if ($_ -match "^([^#][^=]+)=(.*)$") {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

# Verificar variáveis obrigatórias
$requiredVars = @("JIRA_URL", "JIRA_USERNAME", "JIRA_API_TOKEN", "ORG_ID", "ADMIN_API_KEY")
$missingVars = @()

foreach ($var in $requiredVars) {
    if (-not [Environment]::GetEnvironmentVariable($var)) {
        $missingVars += $var
    }
}

if ($missingVars.Count -gt 0) {
    Write-Host "ERRO: Variáveis de ambiente obrigatórias não configuradas:" -ForegroundColor Red
    $missingVars | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

# Verificar se Docker está rodando
Write-Host "Verificando Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "Docker está rodando ✓" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Docker não está rodando. Inicie o Docker Desktop." -ForegroundColor Red
    exit 1
}

# Construir imagem se não existir
Write-Host "Verificando imagem Docker..." -ForegroundColor Yellow
$imageExists = docker images -q mcp-jira-admin:latest
if (-not $imageExists) {
    Write-Host "Construindo imagem Docker..." -ForegroundColor Yellow
    Set-Location docker
    docker build -t mcp-jira-admin:latest .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: Falha ao construir imagem Docker." -ForegroundColor Red
        exit 1
    }
    Set-Location ..
}

# Iniciar servidor MCP Admin via Docker Compose
Write-Host "Iniciando servidor MCP Admin..." -ForegroundColor Yellow
Set-Location docker
docker-compose up -d
if ($LASTEXITCODE -eq 0) {
    Write-Host "Servidor MCP Admin iniciado na porta 6000 ✓" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha ao iniciar servidor MCP Admin." -ForegroundColor Red
    Set-Location ..
    exit 1
}
Set-Location ..

# Aguardar servidor ficar disponível
Write-Host "Aguardando servidor ficar disponível..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
do {
    Start-Sleep -Seconds 2
    $attempt++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:6000/health" -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "Servidor MCP Admin está disponível ✓" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "Tentativa $attempt/$maxAttempts falhou, tentando novamente..." -ForegroundColor Yellow
        if ($attempt -eq $maxAttempts) {
            Write-Host "ERRO: Servidor MCP Admin não ficou disponível após $maxAttempts tentativas." -ForegroundColor Red
            exit 1
        }
    }
} while ($attempt -lt $maxAttempts)

# Instruções para MCP oficial
Write-Host "`n=== Configuração do MCP Oficial ===" -ForegroundColor Cyan
Write-Host "Para conectar ao MCP oficial da Atlassian, execute:" -ForegroundColor Yellow
Write-Host "npx -y mcp-remote https://mcp.atlassian.com/v1/sse" -ForegroundColor White
Write-Host "`nComplete o login OAuth no browser quando solicitado." -ForegroundColor Yellow

# Status final
Write-Host "`n=== Status dos Serviços ===" -ForegroundColor Green
Write-Host "✓ Servidor MCP Admin: http://localhost:6000" -ForegroundColor Green
Write-Host "✓ Configuração Claude Desktop: config\claude_desktop_config.json" -ForegroundColor Green
Write-Host "✓ Configuração genérica MCP: config\mcp_config.json" -ForegroundColor Green

Write-Host "`n=== Próximos Passos ===" -ForegroundColor Yellow
Write-Host "1. Execute o comando do MCP oficial acima" -ForegroundColor White
Write-Host "2. Configure seu cliente MCP com os arquivos de configuração" -ForegroundColor White
Write-Host "3. Teste com comandos como:" -ForegroundColor White
Write-Host "   - 'Crie uma issue de teste no projeto PROJ'" -ForegroundColor Gray
Write-Host "   - 'Crie o usuário teste@empresa.com'" -ForegroundColor Gray

Write-Host "`nPara parar os serviços, execute: .\scripts\stop_services.ps1" -ForegroundColor Cyan