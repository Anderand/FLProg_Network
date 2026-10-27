@echo off
setlocal
set "MANAGER_DIR=%~dp0"
set "PORTING_DIR=%MANAGER_DIR%..\..\STM32_OTA_PORTABILITY"
set "UPLOADER_DIR=%MANAGER_DIR%..\OTA_APP_FLE4D"
set "BUILD_PYTHON=%UPLOADER_DIR%\build_env_win7\Scripts\python.exe"
set "WEBUI_TOOLS=%MANAGER_DIR%..\..\..\flprog_webui_next\tools"
if not exist "%WEBUI_TOOLS%" set "WEBUI_TOOLS=%MANAGER_DIR%..\..\..\WebUI\tools"
set "PYTHONPATH=%WEBUI_TOOLS%;%PYTHONPATH%"
"%BUILD_PYTHON%" -m PyInstaller --noconfirm --clean --onefile --windowed --name FLProg_STM32_OTA_Manager --paths "%PORTING_DIR%" --paths "%UPLOADER_DIR%" --distpath "%MANAGER_DIR%portable_v6" --workpath "%MANAGER_DIR%build_v7" --specpath "%MANAGER_DIR%build_v7" "%MANAGER_DIR%flprog_stm32_ota_manager.py"
if errorlevel 1 exit /b 1
"%BUILD_PYTHON%" "%MANAGER_DIR%package_unified.py"
if errorlevel 1 exit /b 1
echo Unified manager ready: %MANAGER_DIR%portable_v6
