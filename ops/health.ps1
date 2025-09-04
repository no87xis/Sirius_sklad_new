# ---- health.ps1 ----
param([int]$Port = 8000)
try {
  $code = (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:$Port/docs" -TimeoutSec 3).StatusCode
  "HTTP $code"
} catch { "DOWN" }
# ---- /health.ps1 ----
