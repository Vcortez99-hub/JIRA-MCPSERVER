# Script para testar autenticação JIRA manualmente
# Execute este script para verificar se suas credenciais estão corretas

$jiraUrl = "https://canalrural-devskin.atlassian.net"
$email = "vinicius.cortez03@gmail.com"
$apiToken = "SEU_API_TOKEN_AQUI"  # Substitua pelo seu token real

# Criar string de autenticação
$authString = "${email}:${apiToken}"
$authBytes = [System.Text.Encoding]::ASCII.GetBytes($authString)
$authB64 = [System.Convert]::ToBase64String($authBytes)

# Headers
$headers = @{
    "Authorization" = "Basic $authB64"
    "Content-Type" = "application/json"
    "Accept" = "application/json"
}

Write-Host "🔍 Testando autenticação JIRA..." -ForegroundColor Yellow
Write-Host "URL: $jiraUrl" -ForegroundColor Cyan
Write-Host "Email: $email" -ForegroundColor Cyan
Write-Host ""

try {
    # Testar endpoint /myself
    $response = Invoke-RestMethod -Uri "$jiraUrl/rest/api/3/myself" -Headers $headers -Method Get
    
    Write-Host "✅ Autenticação bem-sucedida!" -ForegroundColor Green
    Write-Host "Nome: $($response.displayName)" -ForegroundColor Green
    Write-Host "Email: $($response.emailAddress)" -ForegroundColor Green
    Write-Host "Account ID: $($response.accountId)" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Erro de autenticação:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host ""
        Write-Host "💡 Possíveis soluções:" -ForegroundColor Yellow
        Write-Host "1. Verifique se o API Token está correto" -ForegroundColor White
        Write-Host "2. Confirme se o email está correto" -ForegroundColor White
        Write-Host "3. Crie um novo API Token em: https://id.atlassian.com/manage-profile/security/api-tokens" -ForegroundColor White
    }
}