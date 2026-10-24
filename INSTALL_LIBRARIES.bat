@echo off
chcp 65001 >nul
setlocal
set "RELEASE_IDE=%~1"
if not defined RELEASE_IDE set "RELEASE_IDE=C:\F-981\FLProg\ideV8"
if not exist "%RELEASE_IDE%\portable\sketchbook\libraries" (
  echo FLProg IDE not found. Pass the IDE directory as the first argument.
  pause
  exit /b 1
)
xcopy "%~dp0Библиотека\FLProg_Network\*" "%RELEASE_IDE%\portable\sketchbook\libraries\FLProg_Network\" /E /I /Y
if errorlevel 1 exit /b 1
xcopy "%~dp0Библиотека\FLProg_WebUI\*" "%RELEASE_IDE%\portable\sketchbook\libraries\FLProg_WebUI\" /E /I /Y
if errorlevel 1 exit /b 1
xcopy "%~dp0Библиотека\Flprog_Modbus\*" "%RELEASE_IDE%\portable\sketchbook\libraries\Flprog_Modbus\" /E /I /Y
if errorlevel 1 exit /b 1
echo Installed. Restart FLProg to refresh its virtual library copy.
pause
