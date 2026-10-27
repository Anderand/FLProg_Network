@echo off
setlocal
cd /d "%~dp0"
"C:\Users\user\AppData\Local\Programs\Python\Python38\python.exe" build_stm32_ota.py --interactive
echo.
pause
