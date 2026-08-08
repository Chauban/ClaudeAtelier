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

rem ---- 1.5 clear stale locks -------------------------------
rem  The card-generating agent runs in a Linux sandbox whose
rem  mount of this folder has no delete permission. Its git
rem  commit succeeds, but git cannot remove the lock files it
rem  made - .git/index.lock, HEAD.lock, objects/maintenance.lock
rem  are left behind on EVERY generated card. Every later sync
rem  then dies on "Unable to create index.lock: File exists"
rem  and cards pile up unpublished with nobody noticing (this
rem  cost ~20 hours and 4 cards on 2026-08-05).
rem  Windows has full delete rights here, so this side cleans up.
rem  A lock older than 5 minutes cannot belong to a live git
rem  process - a commit in this repo takes seconds.
echo   [1.5/4] stale locks
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Get-ChildItem -LiteralPath '%~dp0.git' -Filter *.lock -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { ((Get-Date) - $_.LastWriteTime).TotalMinutes -gt 5 } | ForEach-Object { Write-Output ('removed stale lock: ' + $_.FullName); Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue }" >> "%LOG%" 2>&1

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

rem ---- 3.5 reconcile with remote ---------------------------
rem  GitHub may already hold commits this machine does not have
rem  - edited straight on github.com, or pushed from elsewhere.
rem  A bare push then dies on "remote contains work that you do
rem  not have locally" and keeps dying EVERY run, forever, with
rem  nobody told: on 2026-08-08 it failed three times in a row
rem  and held back three finished cards. Rebase local commits
rem  on top of the remote instead.
rem  On conflict, abort: the tree is left byte-for-byte as it
rem  was and a human merges by hand. Nothing is ever lost.
rem  Runs AFTER commit, so the tree is clean - rebase refuses
rem  to run with unstaged changes.
echo   [3.5/4] reconcile
git pull --rebase origin main >> "%LOG%" 2>&1
if errorlevel 1 (
  echo         CONFLICT - rebase aborted, nothing changed
  echo [%date% %time%] rebase CONFLICT - aborted >> "%LOG%"
  git rebase --abort >> "%LOG%" 2>&1
  goto FAIL
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
echo.
echo     "Unable to create ... index.lock: File exists"
echo         A leftover lock newer than 10 minutes, so it was
echo         not auto-cleared. If no git process is running,
echo         delete .git\index.lock (and HEAD.lock,
echo         .git\objects\maintenance.lock) by hand.
echo   ------------------------------------------------------------
echo.
echo   This window stays open on purpose. Copy the error above.
echo.
pause
exit /b 1
