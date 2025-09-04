# ---- restart.ps1 ----
$ErrorActionPreference = 'Stop'

$Ops = 'D:\Sirius_sklad_new\ops'
$Port = if ($PSBoundParameters.ContainsKey('Port')) { $Port } else { 8000 }

powershell -NoProfile -ExecutionPolicy Bypass -File "$Ops\stop.ps1" | Out-Host
Start-Sleep -Seconds 1
powershell -NoProfile -ExecutionPolicy Bypass -File "$Ops\start.ps1" -Port $Port
# ---- /restart.ps1 ----
