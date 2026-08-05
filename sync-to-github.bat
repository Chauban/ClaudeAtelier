@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem ============================================================
rem  ClaudeAtelier -> GitHub sync  (single script)
rem
rem  Usage:
rem    sync-to-github.bat          manual / double-click
rem                                success -> closes by itself
rem                                failure -> stays open, shows error
rem    sync-to-github.bat auto     for Task Scheduler
rem                                never pauses, appends to sync.log
rem
rem  IMPORTANT: keep this file pure ASCII.
rem  cmd.exe reads .bat byte-by-byte in the OEM codepage; UTF-8
rem  Chinese text shifts its file pointer and shatters the
rem  parser (you get 'ho' / 'you' / 'ain' not-a-command errors).
rem ============================================================

set "REPOURL=https://github.com/Chauban/ClaudeAtelier.git"

set "AUTO="
if /i "%~1"=="auto" set "AUTO=1"

if defined AUTO (
  set "LOG=%~dp0sync.log"
) else (
  set "LOG=%~dp0sync-last-run.log"
)

rem ---- reset / open the log for this run --------------------
if defined AUTO (
  echo ============================================= >> "%LOG%"
  echo [%date% %time%] start >> "%LOG%"
) else (
  echo [%date% %time%] start > "%LOG%"
)

echo.
echo   ClaudeAtelier  --^>  GitHub
echo   %REPOURL%
echo.

rem ---- 0. git present? -------------------------------------
where git >nul 2>&1
if errorlevel 1 (
  echo   [X] git not found. >> "%LOG%"
  echo   [X] git not found.
  echo       Install Git for Windows: https://git-scm.com/download/win
  goto FAIL
)

if not exist ".git" (
  echo   [0/4] git init
  git init >> "%LOG%" 2>&1
  git branch -M main >> "%LOG%" 2>&1
)

rem ---- 1. remote -------------------------------------------
echo   [1/4] remote
git remote get-url origin >nul 2>&1
if errorlevel 1 (
  git remote add origin "%REPOURL%" >> "%LOG%" 2>&1
) else (
  git remote set-url origin "%REPOURL%" >> "%LOG%" 2>&1
)

rem ---- 2. stage --------------------------------------------
echo   [2/4] stage
git add -A >> "%LOG%" 2>&1
if errorlevel 1 goto FAIL

rem ---- 3. commit -------------------------------------------
echo   [3/4] commit
git diff --cached --quiet
if errorlevel 1 (
  git commit -m "sync %date% %time%" >> "%LOG%" 2>&1
) else (
  echo         nothing new to commit
  echo [%date% %time%] nothing new to commit >> "%LOG%"
)

rem ---- 4. push ---------------------------------------------
rem  Always push: there may be local commits from earlier runs
rem  that never made it to GitHub.
echo   [4/4] push
git push -u origin main >> "%LOG%" 2>&1
if errorlevel 1 goto FAIL

echo [%date% %time%] pushed OK >> "%LOG%"
echo.
echo   SUCCESS - pushed. Cloudflare will rebuild in about a minute.
if defined AUTO exit /b 0
rem  brief pause so a human double-clicking sees the result, then close
timeout /t 3 >nul
exit /b 0

:FAIL
echo [%date% %time%] FAILED >> "%LOG%"
if defined AUTO exit /b 1

echo.
echo   ============================================================
echo     PUSH FAILED - the git error is shown below.
echo   ============================================================
echo.
type "%LOG%"
echo.
echo   ------------------------------------------------------------
echo     Common causes:
echo.
echo     "could not read Username" / login window closed
echo         Run this script again and finish the GitHub login.
echo.
echo     "Repository not found"
echo         Wrong URL, or the repo is private and this account
echo         has no access.
echo.
echo     "remote contains work that you do not have locally"
echo         GitHub has commits you do not have. Run:
echo             git pull --rebase origin main
echo         then run this script again.
echo   ------------------------------------------------------------
echo.
echo   This window stays open on purpose. Copy the error above.
echo.
pause
exit /b 1
