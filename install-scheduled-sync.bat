@echo off
chcp 65001 >nul
setlocal
set DIR=%~dp0
set SCRIPT=%DIR%sync-to-github-auto.bat

echo ============================================
echo   安装 ClaudeAtelier 自动同步计划任务
echo ============================================
echo.
echo 将建立两个任务：
echo   1) 每天 23:00 自动 push
echo   2) 每次登录 Windows 后 5 分钟自动 push 一次（补上关机期间漏掉的）
echo.
pause

schtasks /Create /TN "ClaudeAtelier-同步GitHub-每日" /TR "\"%SCRIPT%\"" /SC DAILY /ST 23:00 /F
schtasks /Create /TN "ClaudeAtelier-同步GitHub-登录时" /TR "\"%SCRIPT%\"" /SC ONLOGON /DELAY 0005:00 /F

echo.
echo ---- 当前已注册的任务 ----
schtasks /Query /TN "ClaudeAtelier-同步GitHub-每日"
schtasks /Query /TN "ClaudeAtelier-同步GitHub-登录时"

echo.
echo 装好了。日志会写到 sync.log。
echo 想卸载就跑：schtasks /Delete /TN "ClaudeAtelier-同步GitHub-每日" /F
echo.
pause
