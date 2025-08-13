@echo off
echo Starting Shortcut Coach Main System...
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

REM Run the main system
echo.
echo Starting the main system...
python run_main.py

pause
