@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem ============================================================
rem  ONE-SHOT: reconcile the 2026-08-08 divergence.
rem
rem  Local  had: index.html tab-refetch fix (commit c121878)
rem  GitHub had: index.html mobile-interaction rework (af7d619)
rem  Both rewrote renderDropdowns(); rebase could not auto-merge.
rem  _merged-index.html is the hand-resolved 3-way merge: the
rem  mobile handler bodies placed inside the _bound guard, plus
rem  a refetch skip while the mobile filter sheet is open.
rem
rem  Delete this file and resolve-merge.log once it has run.
rem
rem  IMPORTANT: keep this file pure ASCII - cmd.exe reads .bat
rem  byte-by-byte in the OEM codepage and UTF-8 Chinese shifts
rem  its file pointer, shattering the parser. The Chinese commit
rem  message therefore lives in _commit-msg.txt, which is moved
rem  out of the repo before git add so it never gets committed.
rem ============================================================

set "LOG=%~dp0resolve-merge.log"
set "MSG=%TEMP%\claudeatelier-commit-msg.txt"
echo [%date% %time%] start > "%LOG%"

echo   [1/7] stale locks
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Get-ChildItem -LiteralPath '%~dp0.git' -Filter *.lock -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { ((Get-Date) - $_.LastWriteTime).TotalMinutes -gt 5 } | ForEach-Object { Write-Output ('removed stale lock: ' + $_.FullName); Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue }" >> "%LOG%" 2>&1

echo   [2/7] move commit message out of the repo
move /Y "_commit-msg.txt" "%MSG%" >> "%LOG%" 2>&1
if errorlevel 1 goto FAIL

echo   [3/7] fetch
git fetch origin main >> "%LOG%" 2>&1
if errorlevel 1 goto FAIL

echo   [4/7] merge - a conflict in index.html is expected here
git merge --no-commit --no-ff origin/main >> "%LOG%" 2>&1

echo   [5/7] apply resolved index.html
copy /Y "_merged-index.html" "index.html" >> "%LOG%" 2>&1
if errorlevel 1 goto FAIL
del /F /Q "_merged-index.html" >> "%LOG%" 2>&1

echo   [6/7] commit
git add -A >> "%LOG%" 2>&1
git commit -F "%MSG%" >> "%LOG%" 2>&1
if errorlevel 1 goto FAIL

echo   [7/7] push
git push origin main >> "%LOG%" 2>&1
if errorlevel 1 goto FAIL

del /F /Q "%MSG%" >nul 2>&1
echo [%date% %time%] pushed OK >> "%LOG%"
echo.
echo   SUCCESS - merged and pushed. Cloudflare rebuilds in a minute.
timeout /t 5 >nul
exit /b 0

:FAIL
echo [%date% %time%] FAILED >> "%LOG%"
echo.
echo   FAILED - the log is below, nothing was pushed.
echo.
type "%LOG%"
echo.
pause
exit /b 1
