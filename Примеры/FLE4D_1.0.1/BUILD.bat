@echo off
setlocal
"C:\Users\user\AppData\Local\Programs\Python\Python38\python.exe" "%~dp0build.py"
if errorlevel 1 (
  echo Build failed. See build.log.
) else (
  echo BIN ready: %~dp0FLE4D_OTA_BLOCK_1_0_1.bin
)
pause
