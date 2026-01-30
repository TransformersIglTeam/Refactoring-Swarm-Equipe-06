$ErrorActionPreference = "Continue"
$logfile = "simple_fix.log"
$env:GIT_EDITOR = "echo" # Avoid interactive editor prompts

function Log-Command {
    param($cmd)
    Write-Output "`n=== Running: $cmd ===" | Out-File -FilePath $logfile -Append -Encoding utf8
    Invoke-Expression "$cmd 2>&1" | Out-File -FilePath $logfile -Append -Encoding utf8
}

Write-Output "Starting Simple Git Fix..." | Out-File -FilePath $logfile -Encoding utf8

# 1. Abort any stuck processes
Log-Command "git rebase --abort"

# 2. Pull with merge (simpler than rebase)
Log-Command "git pull origin toolsmith --no-rebase"

# 3. Check for conflicts
$status = git status
if ($status -match "conflict") {
    Write-Output "Conflict detected. Resolving using local version (ours)..." | Out-File -FilePath $logfile -Append -Encoding utf8
    
    # Resolve known log file conflict by keeping LOCAL version
    Log-Command "git checkout --ours logs/experiment_data.json"
    Log-Command "git add logs/experiment_data.json"
    
    # Try to commit
    Log-Command "git commit -m 'Merge remote changes, keeping local log data'"
}

# 4. Push
Log-Command "git push origin toolsmith"

Write-Output "`nDone." | Out-File -FilePath $logfile -Append -Encoding utf8
