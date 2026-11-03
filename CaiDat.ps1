param([string]$PythonExe = "", [switch]$OfflineOnly)
$ErrorActionPreference = "Stop"
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
Set-Location -LiteralPath $PSScriptRoot
try {
    if (-not $PythonExe) {
        foreach ($candidate in @(@{ Name="py"; Args=@("-3") }, @{ Name="python"; Args=@() })) {
            $launcher = Get-Command $candidate.Name -CommandType Application -ErrorAction SilentlyContinue
            if (-not $launcher) { continue }
            $launcherArgs = $candidate.Args
            $resolved = & $launcher.Source @launcherArgs -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $resolved) { $PythonExe = ($resolved | Select-Object -Last 1); break }
        }
    }
    if (-not $PythonExe) { throw "Can cai Python 3.10+ 64-bit (co Tcl/Tk), sau do chay lai CaiDat.bat." }
    & $PythonExe -c "import sys,struct,tkinter; assert sys.version_info >= (3,10), 'Need Python >=3.10'; assert struct.calcsize('P')==8, 'Need 64-bit Python'"
    if ($LASTEXITCODE -ne 0) { throw "Python khong phu hop hoac thieu Tcl/Tk." }
    $venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $venvPython)) {
        & $PythonExe -m venv (Join-Path $PSScriptRoot ".venv")
        if ($LASTEXITCODE -ne 0) { throw "Khong tao duoc .venv." }
    }
    $env:PATH = (Join-Path $PSScriptRoot ".venv\Scripts") + ";" + $env:PATH
    $wheels = Join-Path $PSScriptRoot "wheels"
    $lock = Join-Path $PSScriptRoot "requirements-offline.lock"
    $installed = $false
    if ((Test-Path -LiteralPath $lock) -and (Test-Path -LiteralPath $wheels)) {
        & $venvPython -m pip install --no-cache-dir --no-index --find-links $wheels -r $lock
        $installed = ($LASTEXITCODE -eq 0)
    }
    if (-not $installed) {
        if ($OfflineOnly) { throw "Wheel offline khong phu hop Python nay. Dung ban Python da kiem thu hoac cai voi Internet." }
        Write-Host "Cai thu vien tu PyPI; buoc nay can Internet."
        & $venvPython -m pip install --no-cache-dir -r (Join-Path $PSScriptRoot "requirements-online.txt")
        if ($LASTEXITCODE -ne 0) { throw "Cai thu vien that bai. Kiem tra Internet/Python va chay lai." }
    }
    & $venvPython -m pip install --no-cache-dir --no-deps --no-build-isolation -e (Join-Path $PSScriptRoot "aero-hand-open\sdk")
    if ($LASTEXITCODE -ne 0) { throw "Cai SDK local that bai." }
    & $venvPython (Join-Path $PSScriptRoot "tools\kiem_tra_cai_dat.py")
    if ($LASTEXITCODE -ne 0) { throw "Kiem tra cai dat chua dat." }
    Write-Host "CAI DAT XONG. Chay ChayGUI.bat. Chua can cam ban tay trong luc cai."
} catch {
    Write-Host ("LOI: " + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
