@echo off
echo Starting Shortcut Coach...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to create the environment.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Note: This program requires administrator privileges for global tracking.
echo If prompted, please allow access.
echo.
py server/main.py
pause 