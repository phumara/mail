@echo off
REM Activate virtual environment and run Django migrations
call .venv\Scripts\activate.bat
python manage.py migrate