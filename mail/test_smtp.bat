@echo off
REM Activate virtual environment and test SMTP connections
call .venv\Scripts\activate.bat
python manage.py test_smtp