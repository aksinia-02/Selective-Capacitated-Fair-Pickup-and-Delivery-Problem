@echo off
setlocal

set params=%*
set TIMEOUT=200

powershell -Command ^
"$p = Start-Process python -ArgumentList 'run_ga.py %params%' -NoNewWindow -PassThru; ^
if ($p.WaitForExit(%TIMEOUT%000)) { exit 0 } else { $p.Kill(); Write-Output 1e9; exit 0 }"

