#!/bin/bash

# Monitoring Deployment Script for Casablanca Insights
# Deploys complete monitoring infrastructure

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MONITORING_DIR="$PROJECT_ROOT/monitoring"
BACKEND_DIR="$PROJECT_ROOT/apps/backend"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        error "Docker is required but not installed"
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is required but not installed"
        exit 1
    fi
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check if required environment variables are set
    if [ -z "$SUPABASE_URL" ]; then
        error "SUPABASE_URL environment variable is not set"
        exit 1
    fi
    
    if [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
        error "SUPABASE_SERVICE_ROLE_KEY environment variable is not set"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Step 1: Setup monitoring configuration
setup_monitoring_config() {
    log "Step 1: Setting up monitoring configuration"
    log "==========================================="
    
    cd "$PROJECT_ROOT"
    
    # Run monitoring setup script
    if python3 "$PROJECT_ROOT/scripts/setup_monitoring.py"; then
        success "Monitoring configuration setup completed"
    else
        error "Monitoring configuration setup failed"
        exit 1
    fi
    
    # Verify configuration files were created
    if [ -d "$MONITORING_DIR" ]; then
        log "Monitoring configuration files:"
        ls -la "$MONITORING_DIR"
        success "Monitoring configuration verified"
    else
        error "Monitoring configuration directory not found"
        exit 1
    fi
}

# Step 2: Deploy monitoring services
deploy_monitoring_services() {
    log "Step 2: Deploying monitoring services"
    log "===================================="
    
    cd "$BACKEND_DIR"
    
    # Check if docker-compose.yml exists
    if [ ! -f "docker-compose.yml" ]; then
        error "docker-compose.yml not found in backend directory"
        exit 1
    fi
    
    # Start monitoring services
    log "Starting monitoring services..."
    if docker-compose up -d prometheus grafana elasticsearch kibana filebeat; then
        success "Monitoring services started successfully"
    else
        error "Failed to start monitoring services"
        exit 1
    fi
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Check service status
    log "Checking service status..."
    if docker-compose ps | grep -E "(prometheus|grafana|elasticsearch|kibana)" | grep -q "Up"; then
        success "All monitoring services are running"
    else
        error "Some monitoring services failed to start"
        docker-compose ps
        exit 1
    fi
}

# Step 3: Configure Grafana dashboards
configure_grafana_dashboards() {
    log "Step 3: Configuring Grafana dashboards"
    log "====================================="
    
    # Wait for Grafana to be ready
    log "Waiting for Grafana to be ready..."
    for i in {1..60}; do
        if curl -s http://localhost:3001/api/health &> /dev/null; then
            success "Grafana is ready"
            break
        fi
        if [ $i -eq 60 ]; then
            error "Grafana failed to start within timeout"
            exit 1
        fi
        sleep 2
    done
    
    # Import dashboards
    log "Importing Grafana dashboards..."
    
    # Create dashboard import script
    cat > "$MONITORING_DIR/import_dashboards.py" << 'EOF'
#!/usr/bin/env python3
import requests
import json
import os
from pathlib import Path

def import_dashboards():
    grafana_url = "http://localhost:3001"
    username = "admin"
    password = "admin"
    
    # Login to get session
    session = requests.Session()
    login_response = session.post(
        f"{grafana_url}/api/login",
        json={"user": username, "password": password}
    )
    
    if login_response.status_code != 200:
        print("Failed to login to Grafana")
        return False
    
    # Import dashboards
    dashboards_dir = Path("monitoring/grafana/dashboards")
    
    for dashboard_file in dashboards_dir.glob("*.json"):
        with open(dashboard_file, 'r') as f:
            dashboard_data = json.load(f)
        
        import_response = session.post(
            f"{grafana_url}/api/dashboards/db",
            json=dashboard_data
        )
        
        if import_response.status_code == 200:
            print(f"✅ Imported dashboard: {dashboard_file.name}")
        else:
            print(f"❌ Failed to import dashboard: {dashboard_file.name}")
    
    return True

if __name__ == "__main__":
    import_dashboards()
EOF
    
    # Run dashboard import
    if python3 "$MONITORING_DIR/import_dashboards.py"; then
        success "Grafana dashboards imported successfully"
    else
        warning "Some dashboards may not have been imported"
    fi
}

# Step 4: Setup health checks and alerts
setup_health_checks() {
    log "Step 4: Setting up health checks and alerts"
    log "==========================================="
    
    cd "$PROJECT_ROOT"
    
    # Create health check cron job
    log "Setting up health check cron job..."
    
    # Create health check script
    cat > "$MONITORING_DIR/run_health_checks.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/.."
python3 monitoring/health_monitor.py >> monitoring/health_checks.log 2>&1
EOF
    
    chmod +x "$MONITORING_DIR/run_health_checks.sh"
    
    # Add to crontab (every 5 minutes)
    (crontab -l 2>/dev/null; echo "*/5 * * * * $MONITORING_DIR/run_health_checks.sh") | crontab -
    
    success "Health checks configured"
    
    # Test health checks
    log "Testing health checks..."
    if python3 "$MONITORING_DIR/health_monitor.py"; then
        success "Health checks are working"
    else
        warning "Health checks may have issues"
    fi
}

# Step 5: Setup performance monitoring
setup_performance_monitoring() {
    log "Step 5: Setting up performance monitoring"
    log "========================================"
    
    cd "$PROJECT_ROOT"
    
    # Create performance monitoring cron job
    log "Setting up performance monitoring..."
    
    # Create performance monitoring script
    cat > "$MONITORING_DIR/run_performance_monitor.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/.."
python3 monitoring/performance_monitor.py >> monitoring/performance.log 2>&1
EOF
    
    chmod +x "$MONITORING_DIR/run_performance_monitor.sh"
    
    # Add to crontab (every 15 minutes)
    (crontab -l 2>/dev/null; echo "*/15 * * * * $MONITORING_DIR/run_performance_monitor.sh") | crontab -
    
    success "Performance monitoring configured"
    
    # Test performance monitoring
    log "Testing performance monitoring..."
    if python3 "$MONITORING_DIR/performance_monitor.py"; then
        success "Performance monitoring is working"
    else
        warning "Performance monitoring may have issues"
    fi
}

# Step 6: Setup WebSocket monitoring
setup_websocket_monitoring() {
    log "Step 6: Setting up WebSocket monitoring"
    log "======================================"
    
    cd "$PROJECT_ROOT"
    
    # Create WebSocket monitoring cron job
    log "Setting up WebSocket monitoring..."
    
    # Create WebSocket monitoring script
    cat > "$MONITORING_DIR/run_websocket_monitor.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/.."
python3 monitoring/websocket_monitor.py >> monitoring/websocket.log 2>&1
EOF
    
    chmod +x "$MONITORING_DIR/run_websocket_monitor.sh"
    
    # Add to crontab (every 2 minutes)
    (crontab -l 2>/dev/null; echo "*/2 * * * * $MONITORING_DIR/run_websocket_monitor.sh") | crontab -
    
    success "WebSocket monitoring configured"
    
    # Test WebSocket monitoring
    log "Testing WebSocket monitoring..."
    if python3 "$MONITORING_DIR/websocket_monitor.py"; then
        success "WebSocket monitoring is working"
    else
        warning "WebSocket monitoring may have issues"
    fi
}

# Step 7: Setup Airflow alerts
setup_airflow_alerts() {
    log "Step 7: Setting up Airflow alerts"
    log "================================"
    
    cd "$BACKEND_DIR"
    
    # Check if Airflow is running
    if docker-compose ps | grep -q "airflow"; then
        log "Configuring Airflow alerts..."
        
        # Set Airflow variables for alerts
        if [ -n "$ALERT_WEBHOOK_URL" ]; then
            docker-compose exec airflow-webserver airflow variables set SLACK_WEBHOOK_URL "$ALERT_WEBHOOK_URL"
            success "Airflow Slack webhook configured"
        fi
        
        # Set email alerts
        docker-compose exec airflow-webserver airflow variables set ALERT_EMAILS '["admin@morningmaghreb.com"]'
        success "Airflow email alerts configured"
        
        # Test alert configuration
        log "Testing Airflow alert configuration..."
        if docker-compose exec airflow-webserver airflow variables get SLACK_WEBHOOK_URL; then
            success "Airflow alerts configured successfully"
        else
            warning "Airflow alert configuration may have issues"
        fi
    else
        warning "Airflow not running, skipping Airflow alert configuration"
    fi
}

# Step 8: Generate monitoring summary
generate_monitoring_summary() {
    log "Step 8: Generating monitoring summary"
    log "===================================="
    
    cd "$PROJECT_ROOT"
    
    # Create monitoring summary
    cat > "$MONITORING_DIR/monitoring_summary.md" << EOF
# Casablanca Insights - Monitoring Setup Summary

Generated on: $(date)

## Monitoring Services

### ✅ Deployed Services
- **Prometheus**: Metrics collection and storage
- **Grafana**: Dashboards and visualization
- **Elasticsearch**: Log storage and indexing
- **Kibana**: Log visualization and analysis
- **Filebeat**: Log collection and shipping

### 📊 Dashboards Available
- API Performance Dashboard
- Database Performance Dashboard
- ETL Pipeline Dashboard
- WebSocket Dashboard

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3001 | admin / admin |
| **Kibana** | http://localhost:5601 | - |
| **Prometheus** | http://localhost:9090 | - |
| **Elasticsearch** | http://localhost:9200 | - |

## Health Checks

### Automated Checks
- **API Health**: Every 5 minutes
- **Database Health**: Every 5 minutes
- **WebSocket Health**: Every 2 minutes
- **Performance Monitoring**: Every 15 minutes
- **System Resources**: Every 5 minutes

### Manual Health Check
\`\`\`bash
python3 monitoring/health_monitor.py
\`\`\`

## Performance Monitoring

### Automated Performance Tests
- **API Response Times**: Every 15 minutes
- **Database Query Performance**: Every 15 minutes
- **WebSocket Latency**: Every 2 minutes

### Manual Performance Test
\`\`\`bash
python3 monitoring/performance_monitor.py
\`\`\`

## Alerting

### Alert Channels
- **Slack**: DAG failures, SLA misses, critical errors
- **Email**: System alerts, performance issues
- **WebSocket**: Real-time connection issues

### Alert Types
- **Critical**: System failures, database connectivity issues
- **Warning**: Performance degradation, high error rates
- **Info**: Successful operations, system updates

## Logging

### Log Locations
- **Application Logs**: \`logs/\`
- **Health Check Logs**: \`monitoring/health_checks.log\`
- **Performance Logs**: \`monitoring/performance.log\`
- **WebSocket Logs**: \`monitoring/websocket.log\`

### Log Analysis
- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200

## Maintenance

### Regular Tasks
1. **Daily**: Review health check logs
2. **Weekly**: Analyze performance trends
3. **Monthly**: Review and update dashboards
4. **Quarterly**: Update monitoring thresholds

### Troubleshooting
1. Check service status: \`docker-compose ps\`
2. View service logs: \`docker-compose logs [service]\`
3. Test health checks: \`python3 monitoring/health_monitor.py\`
4. Check performance: \`python3 monitoring/performance_monitor.py\`

## Environment Variables

Required environment variables:
- \`SUPABASE_URL\`: Supabase project URL
- \`SUPABASE_SERVICE_ROLE_KEY\`: Supabase service role key
- \`ALERT_WEBHOOK_URL\`: Slack webhook URL (optional)
- \`SENTRY_DSN\`: Sentry DSN for error tracking (optional)

## Next Steps

1. **Configure Alert Channels**: Set up Slack webhooks and email alerts
2. **Customize Dashboards**: Modify Grafana dashboards for your needs
3. **Set Thresholds**: Adjust performance and health check thresholds
4. **Add Custom Metrics**: Implement custom Prometheus metrics
5. **Setup Backup Monitoring**: Monitor backup processes and storage

---

*Generated automatically by deploy_monitoring.sh*
EOF
    
    success "Monitoring summary generated: $MONITORING_DIR/monitoring_summary.md"
}

# Main execution
main() {
    log "Starting Monitoring Deployment"
    log "============================="
    
    # Check prerequisites
    check_prerequisites
    
    # Step 1: Setup monitoring configuration
    setup_monitoring_config
    
    # Step 2: Deploy monitoring services
    deploy_monitoring_services
    
    # Step 3: Configure Grafana dashboards
    configure_grafana_dashboards
    
    # Step 4: Setup health checks and alerts
    setup_health_checks
    
    # Step 5: Setup performance monitoring
    setup_performance_monitoring
    
    # Step 6: Setup WebSocket monitoring
    setup_websocket_monitoring
    
    # Step 7: Setup Airflow alerts
    setup_airflow_alerts
    
    # Step 8: Generate monitoring summary
    generate_monitoring_summary
    
    log "============================="
    success "Monitoring deployment completed successfully!"
    log ""
    log "📊 Monitoring Services:"
    log "   • Grafana: http://localhost:3001 (admin/admin)"
    log "   • Kibana: http://localhost:5601"
    log "   • Prometheus: http://localhost:9090"
    log ""
    log "📋 Health Checks:"
    log "   • Manual: python3 monitoring/health_monitor.py"
    log "   • Automated: Every 5 minutes via cron"
    log ""
    log "⚡ Performance Monitoring:"
    log "   • Manual: python3 monitoring/performance_monitor.py"
    log "   • Automated: Every 15 minutes via cron"
    log ""
    log "📄 Summary: $MONITORING_DIR/monitoring_summary.md"
    log ""
    log "🎉 Your monitoring infrastructure is ready!"
}

# Run main function
main "$@" 