@echo off
chcp 65001 >nul
setlocal
set "DIR=%~dp0"
set "SCRIPT=%DIR%fetch-ds-originals.bat"

rem ============================================================
rem  Keep this file pure ASCII - cmd.exe reads .bat in the OEM
rem  codepage and UTF-8 Chinese text shatters the parser.
rem ============================================================

echo ============================================================
echo   Install ClaudeAtelier DeepSeek-originals fetch task
echo ============================================================
echo.
echo   DeepSeek cards are rendered on a GitHub Actions runner.
echo   The full-size PNG lives only as a workflow artifact, so
echo   this task pulls it down into Cards\YYYY-MM\.
echo.
echo   Runs hourly. `gh run list` is one cheap API call, and an
echo   hourly cadence recovers quickly from a missed slot.
echo.
echo   IMPORTANT - it must run as YOU, not as SYSTEM.
echo   The gh token is stored per Windows user in the credential
echo   manager. Under SYSTEM the task finds no token and does
echo   nothing, forever, without any visible error.
echo.
echo   Artifacts expire after 90 days. If this machine stays off
echo   longer than that, those originals are lost for good.
echo.
echo   Run fetch-ds-originals.bat manually once first to confirm
echo   gh is logged in.
echo.
pause

schtasks /Delete /TN "ClaudeAtelier-FetchDS" /F >nul 2>&1

rem  /RU %USERNAME% + /IT = run as the interactive user, so gh
rem  can reach the credential store.
schtasks /Create /TN "ClaudeAtelier-FetchDS" /TR "\"%SCRIPT%\" auto" ^
  /SC HOURLY /RU "%USERNAME%" /IT /F

echo.
echo ---- registered task ----
schtasks /Query /TN "ClaudeAtelier-FetchDS"

echo.
echo   Done. Log file: fetch-ds.log
echo.
echo   To uninstall:
echo     schtasks /Delete /TN "ClaudeAtelier-FetchDS" /F
echo.
pause
