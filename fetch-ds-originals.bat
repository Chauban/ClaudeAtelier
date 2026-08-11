@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem ============================================================
rem  Fetch DeepSeek card originals from GitHub Actions artifacts
rem
rem  Cards are rendered inside a throwaway container, so the
rem  full-size PNG only exists as a workflow artifact. This task
rem  brings it home. Artifacts expire after 90 days: if this
rem  machine stays off longer than that, the original is gone
rem  for good.
rem
rem  Usage:
rem    fetch-ds-originals.bat          manual / double-click
rem    fetch-ds-originals.bat auto     for Task Scheduler
rem
rem  IMPORTANT: keep this file pure ASCII.
rem  cmd.exe reads .bat byte-by-byte in the OEM codepage; UTF-8
rem  Chinese text shifts its file pointer and shatters the
rem  parser (you get 'ho' / 'you' / 'ain' not-a-command errors).
rem
rem  This is deliberately NOT part of sync-to-github.bat.
rem  That script is the single writer entry point for git and is
rem  battle-tested; a hanging network download inside it would
rem  put the card pushes at risk, and an expired gh login must
rem  never be able to stop them.
rem ============================================================

set "AUTO="
if /i "%~1"=="auto" set "AUTO=1"

echo.
echo   Fetch DeepSeek originals  --^>  Cards\
echo.

rem ---- locate python ---------------------------------------
set "PY="
for /f "delims=" %%i in ('where python 2^>nul') do if not defined PY set "PY=%%i"
if not defined PY (
  for /f "delims=" %%i in ('where py 2^>nul') do if not defined PY set "PY=%%i"
)
if not defined PY (
  echo   [X] python not found on PATH.
  echo       Install Python 3, or run this task as the user that has it.
  goto FAIL
)

rem ---- gh present? -----------------------------------------
where gh >nul 2>&1
if errorlevel 1 (
  echo   [X] gh not found. Install GitHub CLI: https://cli.github.com
  goto FAIL
)

rem ---- run --------------------------------------------------
rem  gh stores its token per Windows user in the credential
rem  manager. If this task runs as SYSTEM it will silently find
rem  no token and do nothing forever, so the installer registers
rem  it under the interactive account. fetch_ds_originals.py
rem  checks `gh auth status` first and says so loudly.
"%PY%" "%~dp0tools\fetch_ds_originals.py"
if errorlevel 1 goto FAIL

echo.
echo   DONE. Log: fetch-ds.log
if defined AUTO exit /b 0
timeout /t 3 >nul
exit /b 0

:FAIL
echo.
echo   FAILED - see fetch-ds.log
if defined AUTO exit /b 1
echo.
echo   This window stays open on purpose.
pause
exit /b 1
