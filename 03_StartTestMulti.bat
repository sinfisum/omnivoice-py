@echo off
cd /d "%~dp0"
set PYTHON_PATH=%~dp0python_embeded\python.exe

if exist "%PYTHON_PATH%" (
    "%PYTHON_PATH%" test_client_multi.py
) else (
    echo Error: python.exe not found in python_embeded folder.
)

pause