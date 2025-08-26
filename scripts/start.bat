@echo off
setlocal ENABLEDELAYEDEXPANSION

set HOST=%HOST%
if "%HOST%"=="" set HOST=0.0.0.0
set PORT=%PORT%
if "%PORT%"=="" set PORT=8000
set APP=%APP%
if "%APP%"=="" set APP=app:app

if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)

echo [start] Subindo FastAPI em http://%HOST%:%PORT%
python -m uvicorn %APP% --host %HOST% --port %PORT% --reload
