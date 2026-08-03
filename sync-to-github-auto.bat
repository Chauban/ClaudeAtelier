@echo off
chcp 65001 >nul
cd /d "%~dp0"
set LOG=%~dp0sync.log

echo ================================= >> "%LOG%"
echo [%date% %time%] 开始 >> "%LOG%"

if not exist ".git" (
  echo [%date% %time%] 错误：还没有 git 仓库 >> "%LOG%"
  exit /b 1
)

git remote get-url origin >nul 2>&1
if errorlevel 1 (
  echo [%date% %time%] 错误：还没关联远程仓库，请先手动跑一次 sync-to-github.bat >> "%LOG%"
  exit /b 1
)

git add -A >> "%LOG%" 2>&1
git diff --cached --quiet
if not errorlevel 1 (
  echo [%date% %time%] 没有新改动，跳过 >> "%LOG%"
  exit /b 0
)

git commit -m "auto sync %date% %time%" >> "%LOG%" 2>&1
git push origin main >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [%date% %time%] 推送失败 >> "%LOG%"
  exit /b 1
)
echo [%date% %time%] 推送成功 >> "%LOG%"
exit /b 0
