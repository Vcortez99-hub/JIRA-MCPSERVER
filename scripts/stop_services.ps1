# Script para parar os serviços MCP-JIRA

Write-Host "=== Parando Serviços MCP-JIRA ===" -ForegroundColor Yellow

# Parar containers Docker
Write-Host "Parando servidor MCP Admin..." -ForegroundColor Yellow
Set-Location docker
docker-compose down
if ($LASTEXITCODE -eq 0) {
    Write-Host "Servidor MCP Admin parado ✓" -ForegroundColor Green
} else {
    Write-Host "Aviso: Problema ao parar servidor MCP Admin" -ForegroundColor Yellow
}
Set-Location ..

# Limpar containers órfãos se existirem
Write-Host "Limpando containers órfãos..." -ForegroundColor Yellow
docker container prune -f | Out-Null

# Verificar se ainda há containers rodando
$runningContainers = docker ps -q --filter "ancestor=mcp-jira-admin:latest"
if ($runningContainers) {
    Write-Host "Forçando parada de containers restantes..." -ForegroundColor Yellow
    docker stop $runningContainers | Out-Null
    docker rm $runningContainers | Out-Null
}

Write-Host "=== Serviços Parados ===" -ForegroundColor Green
Write-Host "Todos os serviços MCP-JIRA foram parados com sucesso." -ForegroundColor Green

# Informações sobre o MCP oficial
Write-Host "`nNota: O MCP oficial da Atlassian (se estiver rodando) deve ser parado manualmente." -ForegroundColor Cyan
Write-Host "Verifique os processos do seu cliente MCP (Claude Desktop, VS Code, etc.)" -ForegroundColor Cyan