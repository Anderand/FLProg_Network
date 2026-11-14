@echo off
setlocal
set "DESIGNER_DIR=%~dp0"
start "FLProg Web UI Designer" /min python "%DESIGNER_DIR%server.py" 8765
timeout /t 1 /nobreak >nul
start "" "http://127.0.0.1:8765"
