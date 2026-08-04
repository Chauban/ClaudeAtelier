@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem ============================================================
rem  IMPORTANT: keep this file pure ASCII.
rem  cmd.exe reads .bat byte-by-byte in the OEM codepage; UTF-8
rem  Chinese text shifts its file pointer and shatters the
rem  parser (you get 'ho' / 'you' / 'ain' not-a-command errors).
rem ============================================================

set "REPOURL=https://github.com/Chauban/ClaudeAtelier.git"

echo.
echo   ClaudeAtelier  --^>  GitHub
echo   %REPOURL%
echo.

where git >nul 2>&1
if errorlevel 1 (
  echo   [X] git not found.
  echo       Install Git for Windows: https://git-scm.com/download/win
  echo.
  pause
  exit /b 1
)

if not exist ".git" (
  echo   [0/4] git init
  git init
  git branch -M main
  echo.
)

echo   [1/4] remote
git remote get-url origin >nul 2>&1
if errorlevel 1 (
  git remote add origin "%REPOURL%"
) else (
  git remote set-url origin "%REPOURL%"
)
git remote get-url origin
echo.

echo   [2/4] stage
git add -A
echo.

echo   [3/4] commit
git diff --cached --quiet
if errorlevel 1 (
  git commit -m "sync %date% %time%"
) else (
  echo         nothing new, skipped
)
echo.

echo   [4/4] push
git push -u origin main
if errorlevel 1 goto FAIL

echo.
echo   ============================================================
echo     SUCCESS - pushed to GitHub.
echo     Now open the Cloudflare build page and click "Retry build".
echo   ============================================================
echo.
pause
exit /b 0

:FAIL
echo.
echo   ============================================================
echo     PUSH FAILED - read the git error printed above.
echo.
echo     "could not read Username" / login window closed
echo         Just run this script again and finish the GitHub login.
echo.
echo     "Repository not found"
echo         Wrong URL, or the repo is private and this account
echo         has no access.
echo.
echo     "remote contains work that you do not have locally"
echo         The GitHub repo is NOT empty (README was checked at
echo         creation). Force push over it with:
echo             git push -u origin main --force
echo   ============================================================
echo.
pause
exit /b 1
