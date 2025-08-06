# 🚀 Casablanca Insights - Complete Setup Guide

This guide will help you set up the Casablanca Insights project from scratch on a fresh machine.

## 📋 Prerequisites

Before running the setup, ensure you have the following installed:

### System Dependencies
- **Git** - Version control
- **Python 3.8+** - Backend development
- **Node.js 18+** - Frontend development
- **npm** - Package manager
- **Docker** (optional) - Containerized development
- **Docker Compose** (optional) - Multi-container orchestration

### Required Services
- **Supabase Account** - Database and authentication
- **OpenAI API Key** (optional) - AI features
- **SendGrid API Key** (optional) - Email notifications
- **Stripe Keys** (optional) - Payment processing

## 🚀 Quick Start

### Option 1: One-Command Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd Casablanca-Insights

# Run the master setup script
./setup.sh
```

### Option 2: Step-by-Step Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd Casablanca-Insights

# 2. Run the complete setup script
./scripts/setup/complete_setup.sh

# 3. Start development servers
./setup.sh --start
```

## 📁 Script Overview

### Master Setup Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup.sh` | Master setup script | `./setup.sh [options]` |
| `scripts/setup/complete_setup.sh` | Complete environment setup | `./scripts/setup/complete_setup.sh` |
| `scripts/test/test_complete_setup.py` | Validate setup | `python3 scripts/test/test_complete_setup.py` |

### Setup Options

```bash
# Full setup (default)
./setup.sh

# Quick setup (skip tests and database)
./setup.sh --quick

# Run tests only
./setup.sh --test-only

# Validate existing setup
./setup.sh --validate-only

# Docker setup
./setup.sh --docker

# Production setup
./setup.sh --production

# Start development servers
./setup.sh --start
```

## 🔧 Environment Configuration

### 1. Environment Variables

The setup will create a `.env` file from the template. Edit it with your actual values:

```bash
# Copy environment template
cp env.template .env

# Edit the file with your values
nano .env
```

### 2. Required Environment Variables

```bash
# Supabase Configuration (Required)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Optional Services
OPENAI_API_KEY=your_openai_api_key
SENDGRID_API_KEY=your_sendgrid_api_key
STRIPE_SECRET_KEY=your_stripe_secret_key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
```

### 3. Supabase Setup

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Get your project URL and anon key from the project settings
3. Add them to your `.env` file
4. Run the database setup:

```bash
# Set up database schema
python3 scripts/setup/setup_supabase_database.py
```

## 🏗️ Project Structure

```
Casablanca-Insights/
├── apps/
│   ├── backend/          # FastAPI backend
│   ├── web/             # Next.js frontend
│   └── mobile/          # React Native mobile app
├── packages/
│   └── shared/          # Shared components and utilities
├── scripts/
│   ├── setup/           # Setup scripts
│   ├── deployment/      # Deployment scripts
│   ├── test/            # Test scripts
│   └── maintenance/     # Maintenance scripts
├── database/            # Database schemas and migrations
├── docs/               # Documentation
└── setup.sh            # Master setup script
```

## 🧪 Testing the Setup

### Run All Tests

```bash
# Run comprehensive tests
./setup.sh --test-only

# Or run the test script directly
python3 scripts/test/test_complete_setup.py
```

### Manual Validation

```bash
# Check Python environment
source .venv/bin/activate
python -c "import fastapi, supabase, uvicorn; print('✅ Python environment OK')"

# Check Node.js environment
npm list --depth=0

# Check environment variables
python3 -c "import os; print('Supabase URL:', os.getenv('NEXT_PUBLIC_SUPABASE_URL')[:20] + '...' if os.getenv('NEXT_PUBLIC_SUPABASE_URL') else 'Not set')"
```

## 🚀 Starting Development

### Start All Servers

```bash
# Start both frontend and backend
./setup.sh --start
```

### Start Individual Servers

```bash
# Backend only
cd apps/backend
source ../../.venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend only
cd apps/web
npm run dev
```

### Using Make Commands

```bash
# Start backend
make start-backend

# Start frontend
make start-frontend

# Health check
make health-check
```

## 🐳 Docker Setup (Optional)

### Start with Docker

```bash
# Build and start all services
cd apps/backend
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Services

- **API** - FastAPI backend (port 8000)
- **PostgreSQL** - Database (port 5432)
- **Redis** - Cache (port 6379)
- **Celery Worker** - Background tasks
- **Flower** - Task monitoring (port 5555)
- **Prometheus** - Metrics (port 9090)
- **Grafana** - Dashboards (port 3001)

## 🔍 Troubleshooting

### Common Issues

#### 1. Python Dependencies Not Found

```bash
# Reinstall Python dependencies
source .venv/bin/activate
pip install -r apps/backend/requirements.txt
```

#### 2. Node.js Dependencies Not Found

```bash
# Reinstall Node.js dependencies
npm install
cd apps/web && npm install && cd ../..
cd apps/mobile && npm install && cd ../..
```

#### 3. Environment Variables Not Loading

```bash
# Check if .env file exists
ls -la .env

# Reload environment variables
export $(cat .env | grep -v '^#' | xargs)
```

#### 4. Database Connection Issues

```bash
# Test Supabase connection
python3 -c "
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()
supabase = create_client(os.getenv('NEXT_PUBLIC_SUPABASE_URL'), os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY'))
print('Connection successful')
"
```

#### 5. Port Conflicts

```bash
# Kill processes on ports 8000 and 3000
make kill-ports

# Or manually
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Debug Mode

```bash
# Run setup with verbose output
./scripts/setup/complete_setup.sh --verbose

# Run tests with detailed output
python3 scripts/test/test_complete_setup.py --verbose
```

## 📚 Additional Resources

### Documentation

- [README.md](README.md) - Main project documentation
- [CASABLANCA_INSIGHTS_SETUP_GUIDE.md](CASABLANCA_INSIGHTS_SETUP_GUIDE.md) - Detailed setup guide
- [DEPLOYMENT_QUICK_REFERENCE.md](DEPLOYMENT_QUICK_REFERENCE.md) - Deployment instructions

### Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/setup/setup_supabase_integration.sh` | Supabase integration setup |
| `scripts/setup/setup_supabase_database.py` | Database schema setup |
| `scripts/deployment/deploy.sh` | Production deployment |
| `scripts/test/test_supabase_connection.py` | Database connection test |

### Development Workflow

1. **Setup**: Run `./setup.sh`
2. **Development**: Run `./setup.sh --start`
3. **Testing**: Run `./setup.sh --test-only`
4. **Validation**: Run `./setup.sh --validate-only`
5. **Deployment**: Run `./setup.sh --production`

## 🎯 Success Criteria

After running the setup, you should have:

- ✅ Python virtual environment with all dependencies
- ✅ Node.js dependencies installed
- ✅ Environment variables configured
- ✅ Database connection working
- ✅ Backend server starting successfully
- ✅ Frontend build working
- ✅ All tests passing
- ✅ Development servers accessible

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs**: Look for error messages in the setup output
2. **Run validation**: `./setup.sh --validate-only`
3. **Check prerequisites**: Ensure all system dependencies are installed
4. **Review environment**: Verify your `.env` file is correctly configured
5. **Check documentation**: Review the detailed guides in the `docs/` directory

## 🚀 Next Steps

Once setup is complete:

1. **Explore the application**: Visit http://localhost:3000
2. **Check the API**: Visit http://localhost:8000/docs
3. **Review the code**: Explore the project structure
4. **Run tests**: Ensure everything is working
5. **Start developing**: Make your first changes!

---

**Happy coding! 🎉** 