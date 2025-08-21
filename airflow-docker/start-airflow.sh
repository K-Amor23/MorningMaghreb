#!/bin/bash
echo "🚀 Starting Airflow Stack for Casablanca Insights..."
echo "🐳 Starting Docker containers..."
docker-compose up -d
echo "✅ Airflow stack is ready!"
echo "🌐 Web UI: http://localhost:8080"
