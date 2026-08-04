@echo off
chcp 65001 >nul
setlocal
set "DIR=%~dp0"
set "SCRIPT=%DIR%sync-to-github-auto.bat"

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
echo   Two tasks will be created:
echo     1) daily at 23:00          - push to GitHub
echo     2) 5 min after each logon  - catch up what was missed
echo.
echo   Run sync-to-github.bat manually at least once first,
echo   so the GitHub login is stored. Otherwise these silent
echo   tasks will fail with no visible prompt.
echo.
pause

schtasks /Create /TN "ClaudeAtelier-Sync-Daily" /TR "\"%SCRIPT%\"" /SC DAILY /ST 23:00 /F
schtasks /Create /TN "ClaudeAtelier-Sync-OnLogon" /TR "\"%SCRIPT%\"" /SC ONLOGON /DELAY 0005:00 /F

echo.
echo ---- registered tasks ----
schtasks /Query /TN "ClaudeAtelier-Sync-Daily"
schtasks /Query /TN "ClaudeAtelier-Sync-OnLogon"

echo.
echo   Done. Log file: sync.log
echo.
echo   To uninstall:
echo     schtasks /Delete /TN "ClaudeAtelier-Sync-Daily" /F
echo     schtasks /Delete /TN "ClaudeAtelier-Sync-OnLogon" /F
echo.
pause
