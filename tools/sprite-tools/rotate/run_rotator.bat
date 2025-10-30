@echo off
cd /d "%~dp0"

REM Try to use venv python if available, otherwise system python
if exist "%cd%\..\..\venv\Scripts\python.exe" (
    "%cd%\..\..\venv\Scripts\python.exe" sprite_sheet_rotator.py
) else (
    python sprite_sheet_rotator.py
)

pause