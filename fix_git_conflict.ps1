$ErrorActionPreference = "Continue" # Continue on error as we are resuming
$logfile = "git_conflict_fix_2.log"

function Log-Command {
    param($cmd)
    Write-Output "`n=== Running: $cmd ===" | Out-File -FilePath $logfile -Append -Encoding utf8
    Invoke-Expression "$cmd 2>&1" | Out-File -FilePath $logfile -Append -Encoding utf8
}

Write-Output "Resuming Git Rebase..." | Out-File -FilePath $logfile -Encoding utf8

# Set GIT_EDITOR to a dummy command so it doesn't open vim
$env:GIT_EDITOR = "cmd /c exit 0"

# We previously did checkout and add. If they are already done, these might do nothing or error slightly, which is fine.
Log-Command "git checkout --theirs logs/experiment_data.json"
Log-Command "git add logs/experiment_data.json"

Log-Command "git rebase --continue"

# If rebase finishes, push.
Log-Command "git push origin toolsmith"

Write-Output "`nDone." | Out-File -FilePath $logfile -Append -Encoding utf8
