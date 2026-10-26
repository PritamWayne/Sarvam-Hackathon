# Git synchronization script for Sarvam project
param(
    [switch]$Watch,
    [int]$IntervalSeconds = 10,
    [string]$RemoteUrl = ""
)

if ($RemoteUrl -ne "") {
    $existingRemote = git remote get-url origin 2>$null
    if ($LASTEXITCODE -eq 0) {
        git remote set-url origin $RemoteUrl
        Write-Host "Updated git remote 'origin' to $RemoteUrl" -ForegroundColor Cyan
    } else {
        git remote add origin $RemoteUrl
        Write-Host "Added git remote 'origin' as $RemoteUrl" -ForegroundColor Cyan
    }
}

function Sync-Git {
    # Check for changes
    $status = git status --porcelain
    if ($status) {
        $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        Write-Host "[$timestamp] Detected changes from active agent / local edits..." -ForegroundColor Yellow
        git add -A
        git commit -m "sync: auto-commit updates from agent ($timestamp)"
        
        $hasRemote = git remote get-url origin 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Pushing to origin/main..." -ForegroundColor Cyan
            git push -u origin main
        } else {
            Write-Host "Changes committed locally. Configure remote 'origin' to push to GitHub." -ForegroundColor Green
        }
    } else {
        if (-not $Watch) {
            Write-Host "Working directory is clean. No new changes to commit." -ForegroundColor Green
        }
    }
}

Sync-Git

if ($Watch) {
    Write-Host "Watching for changes every $IntervalSeconds seconds... (Press Ctrl+C to stop)" -ForegroundColor Magenta
    while ($true) {
        Start-Sleep -Seconds $IntervalSeconds
        Sync-Git
    }
}
