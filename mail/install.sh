#!/bin/bash

# Email Marketing System Installation Script

echo "🚀 Installing Email Marketing System..."

# Check if Python 3.11+ is installed
python_version=$(python --version 2>&1 | awk '{print $2}' | cut -d'.' -f1,2)
if python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "✅ Python $python_version found"
else
    echo "❌ Python 3.11+ is required. Please install Python 3.11 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Check if PostgreSQL is running
if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "✅ PostgreSQL is running"
else
    echo "⚠️ PostgreSQL not detected. Please start PostgreSQL or use Docker:"
    echo "   docker-compose up -d db"
fi

# Check if Redis is running
if redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "⚠️ Redis not detected. Please start Redis or use Docker:"
    echo "   docker-compose up -d redis"
fi

# Run Django migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Creating admin user..."
echo "Please create a superuser account:"
python manage.py createsuperuser

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "🎉 Installation completed!"
echo ""
echo "To start the development server:"
echo "   python manage.py runserver"
echo ""
echo "To start with Docker (recommended for production):"
echo "   docker-compose up -d"
echo ""
echo "To test SMTP connections:"
echo "   python manage.py test_smtp"
echo ""
echo "Access the admin interface at: http://localhost:8000/admin/"
echo "SMTP Dashboard at: http://localhost:8000/campaigns/smtp-dashboard/"