# Script thêm MCP server "simulation" vào Claude config
$configPath = "$env:USERPROFILE\.claude.json"

# Đọc file config
$json = Get-Content $configPath -Raw | ConvertFrom-Json

# Kiểm tra nếu chưa có mcpServers ở root level
if (-not $json.PSObject.Properties["mcpServers"]) {
    $json | Add-Member -MemberType NoteProperty -Name "mcpServers" -Value ([PSCustomObject]@{})
}

# Thêm simulation server
$simulationServer = [PSCustomObject]@{
    type = "http"
    url  = "http://192.168.100.6:8766/mcp/"
}

$json.mcpServers | Add-Member -MemberType NoteProperty -Name "simulation" -Value $simulationServer -Force

# Ghi lại file
$json | ConvertTo-Json -Depth 20 | Set-Content $configPath -Encoding UTF8

Write-Host "✅ Đã thêm MCP server 'simulation' vào Claude config thành công!" -ForegroundColor Green
Write-Host "   URL: http://192.168.100.6:8766/mcp/" -ForegroundColor Cyan
Write-Host ""
Write-Host "➡️  Vui lòng KHỞI ĐỘNG LẠI ứng dụng Claude để MCP có hiệu lực." -ForegroundColor Yellow
