param(
    # [string]$ProductJsonPath = "$env:RobotVsCode\resources\app\product.json"
    [string]$ProductJsonPath = "C:/MyData/4.RobotFramework/Robot-ws/Github/RobotFramework_AIO/install/product.json"
)

# Validate file exists
if (-not (Test-Path $ProductJsonPath)) {
    Write-Error "File not found: $ProductJsonPath"
    exit 1
}

# Read & parse JSON
$json = Get-Content $ProductJsonPath -Raw | ConvertFrom-Json
$proposals = $json.extensionEnabledApiProposals

if ($null -ne $proposals.'GitHub.copilot') {

    $proposals.'GitHub.copilot' = @(
        "inlineCompletionsAdditions"
        "interactive"
        "interactiveUserActions"
        "terminalDataWriteEvent"
    )

    $proposals.'GitHub.copilot-nightly' = @(
        "inlineCompletionsAdditions"
        "interactive"
        "interactiveUserActions"
        "terminalDataWriteEvent"
    )

    # Write back JSON (important for deep structure)
    $json | ConvertTo-Json -Depth 100 | Set-Content $ProductJsonPath -Encoding UTF8

    Write-Host "Updated GitHub Copilot proposals in $ProductJsonPath"
}
else {
    Write-Host "GitHub.copilot not found in $ProductJsonPath, no changes made"
}
