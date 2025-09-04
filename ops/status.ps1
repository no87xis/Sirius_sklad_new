# ---- status.ps1 ----
$ErrorActionPreference = 'Stop'
$LogDir  = 'D:\Sirius_sklad_new\logs'
$PidFile = Join-Path $LogDir 'uvicorn.pid'

if (Test-Path $PidFile) {
  $serverPid = (Get-Content $PidFile) -as [int]
  $alive = Get-Process -Id $serverPid -ErrorAction SilentlyContinue
  "PID=$serverPid STATUS=" + ($(if ($alive) {'RUNNING'} else {'DEAD'}))
} else {
  "STATUS=STOPPED"
}

$last = Get-ChildItem $LogDir uvicorn_*.log -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1
if ($last) {
  "`nLOG: $($last.FullName)`n---"
  Get-Content $last.FullName -Tail 40 -Encoding UTF8
}
# ---- /status.ps1 ----
