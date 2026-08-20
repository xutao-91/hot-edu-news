[CmdletBinding()]
param(
    [switch]$SkipPull,
    [switch]$SkipPush
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'

$repoPath = $PSScriptRoot
$pythonPath = Join-Path $repoPath '.venv\Scripts\python.exe'
$logDir = Join-Path $repoPath 'logs'
$logPath = Join-Path $logDir ("daily-{0}.log" -f (Get-Date -Format 'yyyy-MM-dd'))
$mutex = [Threading.Mutex]::new($false, 'Local\HotEduNewsDaily')
$hasMutex = $false
$transcriptStarted = $false

try {
    $hasMutex = $mutex.WaitOne(0)
    if (-not $hasMutex) {
        throw 'Another hot-edu-news daily run is already active.'
    }

    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    Start-Transcript -Path $logPath -Append | Out-Null
    $transcriptStarted = $true
    Set-Location -LiteralPath $repoPath

    if (-not (Test-Path -LiteralPath $pythonPath)) {
        throw "Python environment not found: $pythonPath"
    }

    Write-Host "[$(Get-Date -Format o)] Starting daily pipeline"

    if (-not $SkipPull) {
        & git pull --ff-only origin main
        if ($LASTEXITCODE -ne 0) { throw 'git pull failed' }
    }

    & $pythonPath run_crawlers.py
    $crawlExit = $LASTEXITCODE

    $crawlSummaryPath = Join-Path $repoPath 'data\cache\last_crawl.json'
    if (-not (Test-Path -LiteralPath $crawlSummaryPath)) {
        throw 'Crawler did not produce data/cache/last_crawl.json'
    }
    $crawlSummary = Get-Content -LiteralPath $crawlSummaryPath -Raw | ConvertFrom-Json
    if ($crawlSummary.sources_failed -ge $crawlSummary.sources_total) {
        throw 'All crawler sources failed; refusing to publish.'
    }
    if ($crawlExit -ne 0) {
        Write-Warning "$($crawlSummary.sources_failed) source(s) failed; successful sources will continue."
    }

    & $pythonPath translate.py
    if ($LASTEXITCODE -ne 0) { throw 'Title processing failed' }

    & $pythonPath generate_html.py
    if ($LASTEXITCODE -ne 0) { throw 'HTML generation failed' }

    & git add -- data/cache data/raw data/translated docs public index.html rss.xml
    if ($LASTEXITCODE -ne 0) { throw 'git add failed' }

    & git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host 'No publishable changes; nothing to commit.'
        exit 0
    }
    if ($LASTEXITCODE -ne 1) { throw 'Unable to inspect staged changes' }

    $message = 'Daily update: {0} | {1} new article(s), {2} failed source(s)' -f `
        (Get-Date -Format 'yyyy-MM-dd HH:mm'), `
        $crawlSummary.new_articles, `
        $crawlSummary.sources_failed
    & git commit -m $message
    if ($LASTEXITCODE -ne 0) { throw 'git commit failed' }

    if (-not $SkipPush) {
        & git push origin main
        if ($LASTEXITCODE -ne 0) { throw 'git push failed' }
    }

    Write-Host "[$(Get-Date -Format o)] Daily pipeline completed"
}
finally {
    if ($transcriptStarted) {
        Stop-Transcript | Out-Null
    }
    if ($hasMutex) {
        $mutex.ReleaseMutex()
    }
    $mutex.Dispose()
}
