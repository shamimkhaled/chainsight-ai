#!/bin/bash

# Setup script for development environment

echo "Setting up ChainSight AI development environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your configuration values."
fi

# Run migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py createsuperuser

# Seed initial data
echo "Seeding initial data..."
python scripts/seed_data.py

echo "Development environment setup completed!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "To start Celery worker (in separate terminal):"
echo "  source venv/bin/activate"
echo "  celery -A config worker -l info"
echo ""
echo "To start Celery beat (in separate terminal):"
echo "  source venv/bin/activate"
echo "  celery -A config beat -l info"