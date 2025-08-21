#!/bin/bash

echo "🚀 Starting Airflow Stack for Casablanca Insights..."

# Generate Fernet key for Airflow
echo "🔑 Generating Fernet key..."
FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo "Generated Fernet key: $FERNET_KEY"

# Update docker-compose.yml with the Fernet key
echo "📝 Updating docker-compose.yml with Fernet key..."
sed -i.bak "s/your-fernet-key-here/$FERNET_KEY/g" docker-compose.yml

# Create .env file for Airflow
echo "📄 Creating .env file..."
cat > .env << EOF
AIRFLOW_UID=50000
AIRFLOW_GID=0
AIRFLOW__CORE__FERNET_KEY=$FERNET_KEY
EOF

# Start the stack
echo "🐳 Starting Docker containers..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Initialize Airflow database
echo "🗄️ Initializing Airflow database..."
docker-compose exec airflow-webserver airflow db init

# Create admin user
echo "👤 Creating admin user..."
docker-compose exec airflow-webserver airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@morningmaghreb.com

# Start scheduler
echo "⏰ Starting Airflow scheduler..."
docker-compose exec airflow-webserver airflow scheduler &

echo "✅ Airflow stack is ready!"
echo "🌐 Web UI: http://localhost:8080"
echo "👤 Username: admin"
echo "🔑 Password: admin"
echo ""
echo "📊 Your DAGs will automatically start running on schedule!"
echo "🔄 Data scraping will begin at 6:00 AM UTC daily"
