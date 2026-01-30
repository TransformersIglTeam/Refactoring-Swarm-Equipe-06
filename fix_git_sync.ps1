$ErrorActionPreference = "Continue" # Don't stop immediately, we want to see output of failed commands
$logfile = "git_sync.log"

function Log-Command {
    param($cmd)
    Write-Output "`n=== Running: $cmd ===" | Out-File -FilePath $logfile -Append -Encoding utf8
    Invoke-Expression "$cmd 2>&1" | Out-File -FilePath $logfile -Append -Encoding utf8
}

Write-Output "Starting Git Sync..." | Out-File -FilePath $logfile -Encoding utf8

Log-Command "git fetch origin"
Log-Command "git status"
Log-Command "git pull --rebase origin toolsmith"
Log-Command "git push origin toolsmith"

Write-Output "`nDone." | Out-File -FilePath $logfile -Append -Encoding utf8
