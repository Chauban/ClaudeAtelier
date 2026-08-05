@echo off
chcp 65001 >nul
setlocal
set "DIR=%~dp0"
set "SCRIPT=%DIR%sync-to-github.bat"

rem ============================================================
rem  Keep this file pure ASCII - cmd.exe reads .bat in the OEM
rem  codepage and UTF-8 Chinese text shatters the parser.
rem  Task names are ASCII too, so schtasks /Query and /Delete
rem  always match regardless of console codepage.
rem ============================================================

echo ============================================================
echo   Install ClaudeAtelier auto-sync scheduled tasks
echo ============================================================
echo.
echo   The card-generating agent only commits locally - it has no
echo   GitHub credentials. These tasks do the pushing.
echo.
echo   Two tasks will be created:
echo     1) every 15 minutes        - push whatever is committed
echo     2) 5 min after each logon  - catch up what was missed
echo.
echo   A push with nothing new is a no-op: no commit reaches
echo   GitHub, so Cloudflare does not rebuild and no build
echo   minutes are burned.
echo.
echo   Run sync-to-github.bat manually at least once first,
echo   so the GitHub login is stored. Otherwise these silent
echo   tasks will fail with no visible prompt.
echo.
echo   Run this installer AS ADMINISTRATOR - the ONLOGON task
echo   cannot be created otherwise.
echo.
pause

rem ---- remove the old daily task if it is still around -------
schtasks /Delete /TN "ClaudeAtelier-Sync-Daily" /F >nul 2>&1

schtasks /Create /TN "ClaudeAtelier-Sync-Every15Min" /TR "\"%SCRIPT%\" auto" /SC MINUTE /MO 15 /F
schtasks /Create /TN "ClaudeAtelier-Sync-OnLogon" /TR "\"%SCRIPT%\" auto" /SC ONLOGON /DELAY 0005:00 /F

echo.
echo ---- registered tasks ----
schtasks /Query /TN "ClaudeAtelier-Sync-Every15Min"
schtasks /Query /TN "ClaudeAtelier-Sync-OnLogon"

echo.
echo   Done. Log file: sync.log
echo.
echo   To uninstall:
echo     schtasks /Delete /TN "ClaudeAtelier-Sync-Every15Min" /F
echo     schtasks /Delete /TN "ClaudeAtelier-Sync-OnLogon" /F
echo.
pause
