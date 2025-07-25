# Casablanca Insights - Development Makefile

.PHONY: start-backend start-frontend start-both kill-ports health-check

# Start Backend Server
start-backend:
	@echo "🚀 Starting Casablanca Insights Backend..."
	cd apps/backend && uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Start Frontend Server
start-frontend:
	@echo "🌐 Starting Casablanca Insights Frontend..."
	cd apps/web && npm run dev

# Start Both Servers (in separate terminals)
start-both:
	@echo "🎯 Starting both servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "Use 'make start-backend' and 'make start-frontend' in separate terminals"

# Kill processes on ports 8000 and 3000
kill-ports:
	@echo "🛑 Killing processes on ports 8000 and 3000..."
	-lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	-lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@echo "✅ Ports cleared"

# Health check for both servers
health-check:
	@echo "🏥 Checking server health..."
	@echo "Backend health:"
	@curl -s http://localhost:8000/health || echo "❌ Backend not responding"
	@echo "Frontend health:"
	@curl -s -I http://localhost:3000 | head -1 || echo "❌ Frontend not responding"

# Install dependencies
install-backend:
	@echo "📦 Installing backend dependencies..."
	cd apps/backend && pip install -r requirements.txt

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd apps/web && npm install

install-all: install-backend install-frontend

# Development helpers
dev-setup: kill-ports install-all
	@echo "✅ Development environment ready"
	@echo "Run 'make start-backend' and 'make start-frontend' in separate terminals"

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Help
help:
	@echo "Casablanca Insights Development Commands:"
	@echo ""
	@echo "  start-backend    - Start FastAPI backend server"
	@echo "  start-frontend   - Start Next.js frontend server"
	@echo "  start-both       - Show instructions for starting both servers"
	@echo "  kill-ports       - Kill processes on ports 8000 and 3000"
	@echo "  health-check     - Check health of both servers"
	@echo "  install-backend  - Install Python dependencies"
	@echo "  install-frontend - Install Node.js dependencies"
	@echo "  install-all      - Install all dependencies"
	@echo "  dev-setup        - Full development environment setup"
	@echo "  clean            - Clean up cache files"
	@echo "  help             - Show this help message" 