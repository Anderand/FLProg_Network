@echo off
setlocal
set "OTA_IDE=%~1"
if not defined OTA_IDE set "OTA_IDE=C:\F-981\FLProg\ideV8"
set "OTA_LIBRARY=%OTA_IDE%\portable\sketchbook\libraries\FLProg_Network\src"
if not exist "%OTA_LIBRARY%\flprogNetwork.h" (
  echo FLProg_Network not found. Run this BAT with the FLProg IDE folder as argument.
  pause
  exit /b 1
)
xcopy "%~dp0src\*" "%OTA_LIBRARY%\" /E /I /Y
if errorlevel 1 exit /b 1
echo OTA block library installed. Restart FLProg to refresh its virtual IDE copy.
pause
