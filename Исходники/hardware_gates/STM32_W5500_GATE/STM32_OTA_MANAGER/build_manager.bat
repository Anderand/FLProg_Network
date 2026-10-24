@echo off
setlocal
set "APP_DIR=%~dp0"
set "OTA_DIR=%APP_DIR%..\OTA_APP_FLE4D"
set "VENV=%OTA_DIR%\build_env_win7"
set "PYTHON=%VENV%\Scripts\python.exe"

if not exist "%PYTHON%" (
  echo Existing Python build environment not found:
  echo %PYTHON%
  exit /b 1
)

"%PYTHON%" -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name FLProg_STM32_OTA_Manager ^
  --paths "%OTA_DIR%" ^
  --distpath "%APP_DIR%portable_v5" ^
  --workpath "%APP_DIR%build" ^
  --specpath "%APP_DIR%build" ^
  "%APP_DIR%flprog_stm32_ota_manager.py"
if errorlevel 1 exit /b 1

"%PYTHON%" "%APP_DIR%make_release.py"
if errorlevel 1 exit /b 1

echo.
echo Manager created in:
echo %APP_DIR%portable_v5
echo.
endlocal
