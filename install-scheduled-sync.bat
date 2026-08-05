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
echo   Cards are generated at 00/04/08/12/16/20 and land as a
echo   local commit around :13 - :17 past the hour.
echo.
echo   Two tasks will be created:
echo     1) 00:30 then every 4 hours  - 6 pushes a day, each
echo        about 15 min after a card is committed
echo     2) 5 min after each logon    - catches cards made while
echo        the machine was off and generated late
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

rem ---- remove superseded tasks if they are still around ------
schtasks /Delete /TN "ClaudeAtelier-Sync-Daily" /F >nul 2>&1
schtasks /Delete /TN "ClaudeAtelier-Sync-Every15Min" /F >nul 2>&1

rem  /RI 240 /DU 24:00 = repeat every 240 min for a full day,
rem  i.e. 00:30 04:30 08:30 12:30 16:30 20:30 from ONE task.
schtasks /Create /TN "ClaudeAtelier-Sync" /TR "\"%SCRIPT%\" auto" /SC DAILY /ST 00:30 /RI 240 /DU 24:00 /F
schtasks /Create /TN "ClaudeAtelier-Sync-OnLogon" /TR "\"%SCRIPT%\" auto" /SC ONLOGON /DELAY 0005:00 /F

echo.
echo ---- registered tasks ----
schtasks /Query /TN "ClaudeAtelier-Sync"
schtasks /Query /TN "ClaudeAtelier-Sync-OnLogon"

echo.
echo   Done. Log file: sync.log
echo.
echo   To uninstall:
echo     schtasks /Delete /TN "ClaudeAtelier-Sync" /F
echo     schtasks /Delete /TN "ClaudeAtelier-Sync-OnLogon" /F
echo.
pause
