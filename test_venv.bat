@echo off
REM Test if virtual environment is activated
call .venv\Scripts\activate.bat
python --version
pip list | findstr Django