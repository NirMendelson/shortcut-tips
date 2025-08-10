@echo off
echo Setting up Shortcut Coach development environment...
echo.

REM Check if Python is installed (try both 'python' and 'py' commands)
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python 3.8+ and try again
        pause
        exit /b 1
    ) else (
        echo Python found via 'py' command. Creating virtual environment...
        py -m venv venv
        goto :activate_env
    )
) else (
    echo Python found via 'python' command. Creating virtual environment...
    python -m venv venv
    goto :activate_env
)

:activate_env
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete! To activate the environment in the future:
echo   venv\Scripts\activate.bat
echo.
echo To run Shortcut Coach:
echo   python server/main.py
echo.
pause 