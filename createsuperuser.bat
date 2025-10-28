@echo off
REM Activate virtual environment and create Django superuser
call .venv\Scripts\activate.bat
python manage.py createsuperuser