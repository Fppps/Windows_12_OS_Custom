@echo off
setlocal
cd /d "%~dp0"

echo [1/5] Checking Python...
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found on PATH.
  pause
  exit /b 1
)

if not exist .venv (
  echo [2/5] Creating virtual environment...
  python -m venv .venv
)

call .venv\Scripts\activate.bat

echo [3/5] Installing requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo [4/5] Validating JSON files...
python validate_data.py
if errorlevel 1 (
  echo Validation failed.
  pause
  exit /b 1
)

echo [5/5] Launching Windows 12 Preview supervisor...
python run_preview.py
pause
