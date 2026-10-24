@echo off
setlocal
cd /d "%~dp0"
python tools\fetch_assets.py
pause
