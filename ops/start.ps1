# ---- start.ps1 ----
param([int]$Port = 8000)
$ErrorActionPreference = 'Stop'

$WorkDir   = 'D:\Sirius_sklad_new'
$PythonExe = Join-Path $WorkDir 'venv\Scripts\python.exe'
$LogDir    = Join-Path $WorkDir 'logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# тключаем PyREPL и включаем UTF-8
$env:PYTHON_BASIC_REPL='1'
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'

# араметры запуска
$Stamp   = Get-Date -Format 'yyyyMMdd_HHmmss'
$LogFile = Join-Path $LogDir "uvicorn_$Stamp.log"
$PidFile = Join-Path $LogDir 'uvicorn.pid'
$ArgLine = "-X utf8 -m uvicorn app.main:app --host 0.0.0.0 --port $Port --reload"

# ерез cmd, единый лог, неблокирующий запуск
$CmdLine = "chcp 65001>nul & `"$PythonExe`" $ArgLine >> `"$LogFile`" 2>&1"
$Proc = Start-Process -FilePath $env:ComSpec -ArgumentList '/d','/c', $CmdLine `
  -WorkingDirectory $WorkDir -WindowStyle Hidden -PassThru

$Proc.Id | Out-File -FilePath $PidFile -Encoding ascii
"STARTED PID=$($Proc.Id)`nLOG=$LogFile"
# ---- /start.ps1 ----
