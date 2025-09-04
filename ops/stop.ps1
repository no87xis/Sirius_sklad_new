# ---- stop.ps1 ----
$ErrorActionPreference = 'Stop'
$PidFile = 'D:\Sirius_sklad_new\logs\uvicorn.pid'

if (Test-Path $PidFile) {
  $serverPid = (Get-Content $PidFile) -as [int]
  if ($serverPid) { Stop-Process -Id $serverPid -Force; "STOPPED $serverPid" }
  Remove-Item $PidFile -Force
} else {
  "NO PIDFILE"
}
# ---- /stop.ps1 ----
