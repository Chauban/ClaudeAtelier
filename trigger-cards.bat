@echo off
chcp 65001 >nul
cd /d "%~dp0"
setlocal

rem ============================================================
rem  ClaudeAtelier -> fire a card workflow on GitHub, on time.
rem
rem  Usage:
rem    trigger-cards.bat deepseek-card.yml
rem    trigger-cards.bat deepseek-pro-card.yml
rem  Registered by install-scheduled-trigger.bat.
rem
rem  WHY THIS EXISTS
rem  The workflows already carry a cron. GitHub honours it, but
rem  never on time: 7 measured schedule runs were late by 47 min
rem  to 2 h 33 min, every single one. Scheduled events sit in a
rem  shared queue GitHub explicitly does not guarantee. A
rem  workflow_dispatch does not - it reaches a runner in seconds.
rem
rem  So the local machine keeps the clock and GitHub keeps the
rem  compute. That split is deliberate: the render script is
rem  written fresh by a model every run and nobody reviews it
rem  before it executes, so it stays on a throwaway VM with no
rem  token, never on this machine - where Cards/ holds 465 MB of
rem  originals that exist in no other place (.gitignore keeps
rem  them out of the repo).
rem
rem  IF THIS FAILS, NOTHING BREAKS
rem  The cron in each workflow is kept as a backstop. Machine
rem  asleep, network down, gh logged out - the card still gets
rem  made, just late, which is exactly today's behaviour. So a
rem  failure here degrades, it does not stop the line. That is
rem  why one retry and a log line are enough, and why this
rem  script must never open an issue or touch the repo.
rem
rem  IT DOES NOT TOUCH THE REPO - no git, no staging, no files
rem  inside the tree except trigger.log (which is .gitignore'd).
rem  That is what lets it run at :00 while the Claude agent owns
rem  :09-:17 and the sync task owns :30.
rem
rem  Auth is whatever `gh auth login` stored in the Windows
rem  Credential Manager - a gho_ OAuth token, which has no
rem  expiry date. No PAT is created and no secret is written to
rem  any file here. Because the token lives in the credential
rem  store, the scheduled task must run as this user with "run
rem  only when user is logged on" (schtasks does that by
rem  default when no /RU is given). Do not "fix" that into
rem  /RU SYSTEM - SYSTEM cannot read the token and every run
rem  would fail silently.
rem
rem  IMPORTANT: keep this file pure ASCII and CRLF.
rem  cmd.exe reads .bat byte-by-byte in the OEM codepage; UTF-8
rem  Chinese text shifts its file pointer and shatters the
rem  parser. An LF-only .bat silently does nothing at all.
rem ============================================================

set "REPO=Chauban/ClaudeAtelier"
set "LOG=%~dp0trigger.log"
set "OUT=%TEMP%\atelier-trigger-out.txt"
set "WF=%~1"

if "%WF%"=="" (
  echo Usage: trigger-cards.bat ^<workflow-file.yml^>
  echo   e.g. trigger-cards.bat deepseek-card.yml
  exit /b 2
)

where gh >nul 2>&1
if errorlevel 1 (
  call :log "FAIL %WF% - gh not found in PATH"
  exit /b 1
)

gh workflow run "%WF%" --repo "%REPO%" > "%OUT%" 2>&1
if not errorlevel 1 goto OK

rem  One retry only. A second failure is not transient - it is a
rem  logged-out gh or a dead network, and neither is fixed by
rem  waiting. The cron backstop covers it.
timeout /t 20 /nobreak >nul
gh workflow run "%WF%" --repo "%REPO%" > "%OUT%" 2>&1
if not errorlevel 1 goto OK

call :log "FAIL %WF% - dispatch failed twice, cron will cover this slot"
type "%OUT%" >> "%LOG%"
exit /b 1

:OK
rem  gh prints the run URL - keep it, it is the whole diagnosis
rem  trail when a card later turns out missing.
call :log "OK   %WF%"
type "%OUT%" >> "%LOG%"
exit /b 0

:log
echo [%DATE% %TIME%] %~1 >> "%LOG%"
goto :eof
