
# Cole sua chave aqui (substitua)


# Testar qual modelo funciona
$models = @(
    "gemini-pro",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash-exp",
    "gemini-exp-1206"
)

foreach ($model in $models) {
    Write-Host "`nTestando: $model" -ForegroundColor Yellow
    
    $url = "https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=$API_KEY"
    $body = @{
        contents = @(
            @{
                parts = @(
                    @{ text = "Olá" }
                )
            }
        )
    } | ConvertTo-Json -Depth 10
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method POST -Body $body -ContentType "application/json"
        Write-Host "✅ FUNCIONA!" -ForegroundColor Green
        break
    } catch {
        Write-Host "❌ Não funciona" -ForegroundColor Red
    }
}
