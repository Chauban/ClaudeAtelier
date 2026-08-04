@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "LOG=%~dp0sync.log"

rem ============================================================
rem  Silent scheduled sync. Keep this file pure ASCII - cmd.exe
rem  reads .bat in the OEM codepage and UTF-8 Chinese text
rem  shatters the parser. See sync-to-github.bat for details.
rem ============================================================

set "REPOURL=https://github.com/Chauban/ClaudeAtelier.git"

echo ============================================= >> "%LOG%"
echo [%date% %time%] start >> "%LOG%"

if not exist ".git" (
  echo [%date% %time%] ERROR: no git repo here >> "%LOG%"
  exit /b 1
)

git remote get-url origin >nul 2>&1
if errorlevel 1 (
  git remote add origin "%REPOURL%" >> "%LOG%" 2>&1
  echo [%date% %time%] added remote origin >> "%LOG%"
)

git add -A >> "%LOG%" 2>&1

git diff --cached --quiet
if not errorlevel 1 (
  echo [%date% %time%] no changes, skipped >> "%LOG%"
  exit /b 0
)

git commit -m "sync %date% %time%" >> "%LOG%" 2>&1
git push origin main >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [%date% %time%] PUSH FAILED - see git output above >> "%LOG%"
  exit /b 1
)

echo [%date% %time%] pushed OK >> "%LOG%"
exit /b 0
