#!/bin/bash
# Setup script to initialize the Django smart-purchase-system backend

cd "$(dirname "$0")" || exit

echo "🔧 Setting up Django backend..."

# Create cache table
echo "📦 Creating Django cache table..."
python manage.py createcachetable

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Load initial data
echo "📊 Loading initial product data..."
python manage.py loaddata backend/products/fixtures/websites.json

# Collect static files (optional, for production)
# python manage.py collectstatic --noinput

echo "✅ Backend setup complete!"
echo ""
echo "To start the development server, run:"
echo "  python manage.py runserver"
