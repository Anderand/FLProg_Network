@echo off
setlocal
cd /d "%~dp0"
title FLProg Web UI Editor

rem Prefer the portable build. It includes Python and needs no installation.
set "FLPROG_WEBUI_EXE=%~dp0portable\FLProg_WebUI_Editor\FLProg_WebUI_Editor.exe"
if exist "%FLPROG_WEBUI_EXE%" (
    start "FLProg Web UI Editor" "%FLPROG_WEBUI_EXE%"
    goto :end
)

py -3 -c "import sys; assert sys.version_info >= (3,7)" >nul 2>nul
if not errorlevel 1 (
    start "" /b powershell.exe -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8766/'"
    py -3 server.py 8766
    if errorlevel 1 pause
    goto :end
)

python -c "import sys; assert sys.version_info >= (3,7)" >nul 2>nul
if not errorlevel 1 (
    start "" /b powershell.exe -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8766/'"
    python server.py 8766
    if errorlevel 1 pause
    goto :end
)

rem FLProg Portable already ships Python for the ESP8266 toolchain.  This
removes a separate Python installation as a prerequisite for the editor.
set "FLPROG_PYTHON=C:\FL\FLProg_9.8.1_Windows_Portable\ideV8\portable\packages\esp8266\tools\python3\3.7.2-post1\python.exe"
if exist "%FLPROG_PYTHON%" (
    start "" /b powershell.exe -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8766/'"
    "%FLPROG_PYTHON%" server.py 8766
    if errorlevel 1 pause
    goto :end
)

echo.
echo Python was not found.
echo Install Python 3, or start FLProg Portable so its bundled Python is available.
echo Then run this file again.
echo.
pause

:end
endlocal
