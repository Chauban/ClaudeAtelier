@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".git" (
  echo [1/4] 初始化本地仓库...
  git init
  git branch -M main
)

git remote get-url origin >nul 2>&1
if errorlevel 1 (
  echo.
  echo 还没有关联 GitHub 远程仓库。
  echo 请先在 GitHub 上建一个空仓库（不要勾选 README），然后把地址贴到下面。
  echo 例：https://github.com/yourname/claude-atelier.git
  echo.
  set /p REPOURL=仓库地址: 
  git remote add origin %REPOURL%
)

echo [2/4] 暂存改动...
git add -A

echo [3/4] 提交...
git diff --cached --quiet && (echo 没有新改动，跳过提交。) || git commit -m "cards: %date% %time%"

echo [4/4] 推送到 GitHub...
git push -u origin main

echo.
echo 完成。
pause
