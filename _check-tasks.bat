@echo off
set "OUT=%~dp0_check-tasks.log"
schtasks /Run /TN "ClaudeAtelier-Sync-Daily" > "%OUT%" 2>&1
timeout /t 12 >nul
schtasks /Query /TN "ClaudeAtelier-Sync-Daily" /FO LIST /V >> "%OUT%" 2>&1
exit /b 0
