# ==========================================
# Auto Free Port 8000 and Run Uvicorn Script
# ==========================================

$ErrorActionPreference = "Stop"

# Step 0: Allow PowerShell script execution temporarily (for this session only)
Set-ExecutionPolicy Bypass -Scope Process -Force

# --- Elevate to admin if needed (auto re-launch)
try {
  $id = [Security.Principal.WindowsIdentity]::GetCurrent()
  $p  = New-Object Security.Principal.WindowsPrincipal($id)
  if (-not $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Re-launching with admin privileges..." -ForegroundColor Yellow
    Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-File","`"$PSCommandPath`"") -Verb RunAs
    exit
  }
} catch {
  Write-Host "Unable to check elevation; continuing (may fail later)." -ForegroundColor Yellow
}

# --- Config
$Port = 8000
$VenvPath = Join-Path $PSScriptRoot "venv"
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
$ReqFile = Join-Path $PSScriptRoot "requirements.txt"
$EnvFile = Join-Path $PSScriptRoot ".env"
$EnvExample = Join-Path $PSScriptRoot ".env.example"

# Step 1: Port usage check and selective termination
Write-Host "`n🔍 Checking if port $Port is in use..." -ForegroundColor Cyan
$netstatOutput = netstat -aon | Select-String ":$Port\s"
if ($netstatOutput) {
  $pids = @()
  foreach ($line in $netstatOutput) {
    $cols = ($line.ToString() -split '\s+') | Where-Object { $_ -ne "" }
    $processId  = $cols[-1]
    if ($processId -match '^\d+$') { $pids += [int]$processId }
  }
  $pids = $pids | Select-Object -Unique
  if ($pids.Count -gt 0) {
    Write-Host "⚠️  Port $Port appears in use by PID(s): $($pids -join ', ')" -ForegroundColor Yellow
    foreach ($processId in $pids) {
      Write-Host "`n📋 Process details for PID $($processId):" -ForegroundColor Green
      try { tasklist /FI ("PID eq " + $processId) } catch {}
      # Terminate only if likely our dev servers
      $procName = (Get-Process -Id $processId -ErrorAction SilentlyContinue).ProcessName
      if ($procName -match 'python' -or $procName -match 'node' -or $procName -match 'uvicorn') {
        Write-Host "🛑 Terminating process $processId ($procName)..." -ForegroundColor Red
        try { Stop-Process -Id $processId -Force -ErrorAction Stop; Write-Host "✅ Process $processId terminated." -ForegroundColor Green } catch {}
      } else {
        Write-Host "⚠️  PID $processId is not python/node/uvicorn; skipping termination for safety." -ForegroundColor Yellow
      }
    }
  }
} else {
  Write-Host "✅ Port $Port is free and ready to use." -ForegroundColor Green
}

# --- Verify port freed (with small retry)
function Test-PortBusy { param($Port)
  try { if (Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue) { return $true } } catch {}
  try { if (netstat -a -n -o | Select-String ":$Port\s" -Quiet) { return $true } } catch {}
  return $false
}
$tries = 5; $ok = $false
for ($i=1; $i -le $tries; $i++) {
  if (-not (Test-PortBusy -Port $Port)) { $ok = $true; break }
  Start-Sleep -Milliseconds 200
}
if (-not $ok) {
  Write-Host "ERROR: Port ${Port} is still in use after retries. Aborting." -ForegroundColor Red
  Write-Host "Hint: Run `netstat -a -n -o | findstr :${Port}` to inspect processes." -ForegroundColor Yellow
  exit 1
}

# --- Ensure virtual environment exists
if (-not (Test-Path $VenvPath)) {
  Write-Host "Creating virtual environment at $VenvPath..."
  try {
    python -m venv $VenvPath
    Write-Host "Virtual environment created."
  } catch {
    Write-Host "Failed to create venv. Ensure Python is on PATH and version is >= 3.8." -ForegroundColor Red
    exit 1
  }
} else {
  Write-Host "Virtual environment already exists."
}

# --- Activate venv in current process
if (Test-Path $ActivateScript) {
  Write-Host "Activating virtual environment..."
  try { & $ActivateScript; Write-Host "Virtual environment activated." } catch {
    Write-Host "Failed to activate venv with Activate.ps1. Falling back to using python from venv." -ForegroundColor Yellow
    $venvPython = Join-Path $VenvPath "Scripts\python.exe"
    if (Test-Path $venvPython) { $env:Path = "$(Split-Path $venvPython);$env:Path" }
  }
} else {
  Write-Host "Activate script not found; proceeding to use python from venv if available." -ForegroundColor Yellow
  $venvPython = Join-Path $VenvPath "Scripts\python.exe"
  if (Test-Path $venvPython) { $env:Path = "$(Split-Path $venvPython);$env:Path" }
}

# --- Upgrade pip and install requirements if present
try { Write-Host "Upgrading pip..."; python -m pip install --upgrade pip > $null 2>&1 } catch {
  Write-Host "Warning: pip upgrade failed or python not available in PATH." -ForegroundColor Yellow
}
if (Test-Path $ReqFile) {
  Write-Host "Installing requirements from requirements.txt..."
  try { python -m pip install -r $ReqFile; Write-Host "Dependencies installed." } catch {
    Write-Host "Failed to install dependencies. Please inspect pip output above." -ForegroundColor Red
  }
} else {
  Write-Host "No requirements.txt found. Skipping dependency install."
}

# --- Ensure .env exists
if (-not (Test-Path $EnvFile)) {
  if (Test-Path $EnvExample) {
    Copy-Item $EnvExample $EnvFile
    Write-Host ".env created from .env.example. Please update sensitive values (for example GEMINI_API_KEY)."
  } else {
    New-Item -Path $EnvFile -ItemType File -Force | Out-Null
    Write-Host "Created empty .env. Please populate it with required variables (for example GEMINI_API_KEY)."
  }
} else {
  Write-Host ".env already exists."
}

# --- Ensure Windows Firewall allows inbound TCP on the selected port
Write-Host "Ensuring Windows Firewall allows inbound TCP ${Port}..."
try {
  netsh advfirewall firewall add rule name="Allow Python ${Port}" dir=in action=allow protocol=TCP localport=${Port} | Out-Null
  Write-Host "Firewall rule ensured (added or already present)."
} catch {
  Write-Host "Warning: failed to add firewall rule for port ${Port}: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 5: Start Uvicorn Server (bind to loopback explicitly)
Write-Host "`n🚀 Starting Uvicorn server on port $Port..." -ForegroundColor Cyan
$env:UVICORN_HOST = "127.0.0.1"
try {
  $uvicornCmd = "uvicorn app.main:app --reload --host 127.0.0.1 --port ${Port}"
  Write-Host "Command: $uvicornCmd"
  Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile","-NoExit","-Command",$uvicornCmd) -WorkingDirectory $PSScriptRoot
} catch {
  Write-Host "Failed to start uvicorn: $($_.Exception.Message)" -ForegroundColor Red
  exit 1
}


