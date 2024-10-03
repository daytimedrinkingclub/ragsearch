#!/bin/sh

# Wait for the database to be ready
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database is ready!"

# Initialize the database if it hasn't been initialized yet
if [ ! -d "migrations" ]; then
    echo "Initializing the database..."
    flask db init
    echo "Database initialized."
fi

# Force a new migration
echo "Creating a new migration..."
flask db migrate -m "Add System model"

# Show current migration status
echo "Current migration status:"
flask db current

# Run database migrations
echo "Running database migrations..."
flask db upgrade
echo "Migration complete."

# Show migration status after upgrade
echo "Migration status after upgrade:"
flask db current

# Seed the database
echo "Seeding the database..."
flask seed-db
echo "Database seeding completed."

# Start the application
echo "Starting the application..."
gunicorn -b 0.0.0.0:5000 run:app