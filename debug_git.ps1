$ErrorActionPreference = "Stop"
try {
    Write-Output "Checking git location..." | Out-File -FilePath git_debug.log -Encoding utf8
    Get-Command git | Select-Object Source | Out-File -FilePath git_debug.log -Append -Encoding utf8
    
    Write-Output "`nChecking git status..." | Out-File -FilePath git_debug.log -Append -Encoding utf8
    git status 2>&1 | Out-File -FilePath git_debug.log -Append -Encoding utf8
    
    Write-Output "`nChecking git remote..." | Out-File -FilePath git_debug.log -Append -Encoding utf8
    git remote -v 2>&1 | Out-File -FilePath git_debug.log -Append -Encoding utf8
} catch {
    Write-Output "Error: $_" | Out-File -FilePath git_debug.log -Append -Encoding utf8
}
