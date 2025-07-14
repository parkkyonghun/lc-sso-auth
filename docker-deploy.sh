#!/bin/bash
# Docker Deployment Script for FastAPI SSO System
# This script provides easy deployment options for Linux/macOS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

echo "========================================"
echo "   FastAPI SSO System - Docker Deploy"
echo "========================================"
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not available"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running"
    echo "Please start Docker service"
    exit 1
fi

print_status "Docker is available and running"
echo

echo "Select deployment option:"
echo "1. Development (SQLite + Redis) - Quick start"
echo "2. PostgreSQL (PostgreSQL + Redis + pgAdmin) - Full database"
echo "3. Production (with Nginx + SSL ready) - Production deployment"
echo "4. Stop all services"
echo "5. View logs"
echo "6. Clean up (remove containers and volumes)"
echo "7. Health check"
echo "8. Create admin user"
echo
read -p "Enter your choice (1-8): " choice

case $choice in
    1)
        echo
        print_info "Starting Development Environment..."
        echo "Services: FastAPI SSO (8000) + Redis (6379)"
        echo
        
        docker-compose up -d
        
        if [ $? -eq 0 ]; then
            echo
            print_status "Development environment started successfully!"
            echo "🌐 API: http://localhost:8000"
            echo "📚 API Docs: http://localhost:8000/docs"
            echo "🔧 Admin: Create admin with './docker-deploy.sh' option 8"
            echo
        else
            print_error "Failed to start services"
            exit 1
        fi
        ;;
        
    2)
        echo
        print_info "Starting PostgreSQL Environment..."
        echo "Services: FastAPI SSO (8000) + PostgreSQL (5432) + Redis (6379) + pgAdmin (5050)"
        echo
        
        docker-compose -f docker-compose.postgres.yml up -d
        
        if [ $? -eq 0 ]; then
            echo
            print_status "PostgreSQL environment started successfully!"
            echo "🌐 API: http://localhost:8000"
            echo "📚 API Docs: http://localhost:8000/docs"
            echo "🗄️ pgAdmin: http://localhost:5050 (admin@sso.local / admin123)"
            echo "🔧 Database: localhost:5432 (sso_user / sso_password / sso_db)"
            echo
        else
            print_error "Failed to start services"
            exit 1
        fi
        ;;
        
    3)
        echo
        print_warning "Production Deployment"
        echo "This requires environment variables to be set."
        echo
        read -p "Do you have JWT keys and secrets configured? (y/n): " confirm
        
        if [[ $confirm != [yY] ]]; then
            echo
            print_warning "Please configure the following environment variables:"
            echo "- JWT_PRIVATE_KEY"
            echo "- JWT_PUBLIC_KEY"
            echo "- SECRET_KEY"
            echo "- REDIS_PASSWORD"
            echo
            echo "See DOCKER_DEPLOYMENT_GUIDE.md for details."
            exit 1
        fi
        
        echo
        print_info "Starting Production Environment..."
        echo "Services: FastAPI SSO (8000) + Redis (6379) + Nginx (80/443)"
        echo
        
        docker-compose -f docker-compose.prod.yml up -d
        
        if [ $? -eq 0 ]; then
            echo
            print_status "Production environment started successfully!"
            echo "🌐 API: http://localhost:8000"
            echo "🌍 Web: http://localhost (via Nginx)"
            echo "📚 API Docs: http://localhost:8000/docs"
            echo
        else
            print_error "Failed to start services"
            exit 1
        fi
        ;;
        
    4)
        echo
        print_info "Stopping all services..."
        docker-compose down 2>/dev/null || true
        docker-compose -f docker-compose.postgres.yml down 2>/dev/null || true
        docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
        print_status "All services stopped."
        echo
        ;;
        
    5)
        echo
        echo "Select service to view logs:"
        echo "1. SSO API"
        echo "2. Redis"
        echo "3. PostgreSQL"
        echo "4. Nginx"
        echo "5. All services (development)"
        echo "6. All services (PostgreSQL)"
        echo "7. All services (production)"
        echo
        read -p "Enter choice (1-7): " logchoice
        
        case $logchoice in
            1) docker-compose logs -f sso-api ;;
            2) docker-compose logs -f redis ;;
            3) docker-compose -f docker-compose.postgres.yml logs -f postgres ;;
            4) docker-compose -f docker-compose.prod.yml logs -f nginx ;;
            5) docker-compose logs -f ;;
            6) docker-compose -f docker-compose.postgres.yml logs -f ;;
            7) docker-compose -f docker-compose.prod.yml logs -f ;;
            *) print_error "Invalid choice" ;;
        esac
        ;;
        
    6)
        echo
        print_warning "WARNING: This will remove all containers, volumes, and data!"
        read -p "Are you sure? (y/n): " confirm
        
        if [[ $confirm != [yY] ]]; then
            echo "Cleanup cancelled."
            exit 0
        fi
        
        echo
        print_info "Cleaning up Docker resources..."
        docker-compose down -v 2>/dev/null || true
        docker-compose -f docker-compose.postgres.yml down -v 2>/dev/null || true
        docker-compose -f docker-compose.prod.yml down -v 2>/dev/null || true
        docker system prune -f
        print_status "Cleanup completed."
        echo
        ;;
        
    7)
        echo
        print_info "Performing health checks..."
        echo
        
        # Check if containers are running
        echo "Container Status:"
        docker-compose ps 2>/dev/null || echo "Development containers not running"
        echo
        
        # Check API health
        echo "API Health Check:"
        if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
            print_status "API is healthy"
        else
            print_error "API is not responding"
        fi
        
        # Check Redis
        echo "Redis Health Check:"
        if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
            print_status "Redis is healthy"
        else
            print_error "Redis is not responding"
        fi
        
        echo
        ;;
        
    8)
        echo
        print_info "Creating admin user..."
        echo
        
        # Check if containers are running
        if ! docker-compose ps | grep -q "Up"; then
            print_error "No containers are running. Please start the environment first."
            exit 1
        fi
        
        docker-compose exec sso-api python create_admin.py
        
        if [ $? -eq 0 ]; then
            print_status "Admin user creation completed!"
        else
            print_error "Failed to create admin user"
        fi
        echo
        ;;
        
    *)
        print_error "Invalid choice. Please select 1-8."
        exit 1
        ;;
esac

echo
echo "📖 For more information, see DOCKER_DEPLOYMENT_GUIDE.md"
echo "🆘 Need help? Check logs with option 5 or visit the documentation."
echo

# Make the script executable
chmod +x "$0" 2>/dev/null || true