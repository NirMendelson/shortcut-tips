@echo off
echo Starting Shortcut Coach Portfolio Demo...
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found, installing packages globally...
)

REM Install required packages
echo Installing required packages...
pip install -r requirements.txt

REM Run the portfolio demo
echo.
echo Starting the demo...
python run_portfolio_demo.py

pause
