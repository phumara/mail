@echo off
REM Email Marketing System Installation Script for Windows

echo 🚀 Installing Email Marketing System...

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

for /f "tokens=2 delims=." %%i in ('python --version 2^>nul') do (
    set "python_major=%%i"
    for /f "tokens=2 delims=." %%j in ('python --version 2^>nul') do (
        set "python_minor=%%j"
        goto :check_version
    )
)

:check_version
if %python_major% lss 3 (
    echo ❌ Python 3.11+ is required. Current version: %python_major%.%python_minor%
    pause
    exit /b 1
)
if %python_major% equ 3 (
    if %python_minor% lss 11 (
        echo ❌ Python 3.11+ is required. Current version: %python_major%.%python_minor%
        pause
        exit /b 1
    )
)

echo ✅ Python %python_major%.%python_minor% found

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo 📚 Installing Python packages...
pip install -r requirements.txt

REM Check if PostgreSQL is running (optional check)
echo 🔍 Checking PostgreSQL status...
pg_isready -h localhost -p 5432 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ PostgreSQL not detected. Please start PostgreSQL or use Docker:
    echo    docker-compose up -d db
) else (
    echo ✅ PostgreSQL is running
)

REM Check if Redis is running (optional check)
echo 🔍 Checking Redis status...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Redis not detected. Please start Redis or use Docker:
    echo    docker-compose up -d redis
) else (
    echo ✅ Redis is running
)

REM Run Django migrations
echo 🗄️ Running database migrations...
python manage.py migrate

REM Create superuser
echo 👤 Creating admin user...
echo Please create a superuser account:
python manage.py createsuperuser

REM Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput

echo.
echo 🎉 Installation completed!
echo.
echo To start the development server:
echo    python manage.py runserver
echo.
echo To start with Docker (recommended for production^):
echo    docker-compose up -d
echo.
echo To test SMTP connections:
echo    python manage.py test_smtp
echo.
echo Access the admin interface at: http://localhost:8000/admin/
echo SMTP Dashboard at: http://localhost:8000/campaigns/smtp-dashboard/
echo.
pause