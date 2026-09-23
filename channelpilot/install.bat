@echo off
title ChannelPilot setup
echo === ChannelPilot setup ===
python --version >nul 2>&1
if errorlevel 1 (
  echo.
  echo [1/3] Python not found. Install Python 3.10 or newer from https://www.python.org/downloads/
  echo       and tick "Add python.exe to PATH" during install. Then run install.bat again.
  pause
  exit /b 1
)
echo [2/3] Installing needed packages...
pip install -r requirements.txt
echo.
echo [3/3] Give the agent a brain (pick ONE):
echo   A. Free and fully local: install Ollama from https://ollama.com/download
echo      then open a terminal and run:  ollama pull llama3.1:8b
echo   B. Or paste an API key into config.yaml (under brain -^> api_key).
echo.
echo Done. Double-click start.bat to launch ChannelPilot.
pause
