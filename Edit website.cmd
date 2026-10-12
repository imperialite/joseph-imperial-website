@echo off
cd /d "%~dp0"
python edit.py
if errorlevel 1 (
  echo.
  echo The editor could not start. Python 3.11 or newer is required.
  pause
)
