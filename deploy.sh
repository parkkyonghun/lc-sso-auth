#!/bin/bash

# SSO Service Deployment Script
# Usage: ./deploy.sh [dev|prod]

set -e

ENVIRONMENT=${1:-dev}
PROJECT_NAME="sso-service"

echo "🚀 Deploying SSO Service in $ENVIRONMENT mode..."

# Function to generate JWT keys
generate_jwt_keys() {
    echo "🔑 Generating JWT keys..."
    
    # Create ssl directory if it doesn't exist
    mkdir -p ssl
    
    # Generate private key
    openssl genrsa -out ssl/jwt_private_key.pem 2048
    
    # Generate public key
    openssl rsa -in ssl/jwt_private_key.pem -pubout -out ssl/jwt_public_key.pem
    
    echo "✅ JWT keys generated successfully"
}

# Function to generate SSL certificates (self-signed for development)
generate_ssl_certs() {
    echo "🔒 Generating SSL certificates..."
    
    mkdir -p ssl
    
    # Generate self-signed certificate for development
    openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    
    echo "✅ SSL certificates generated successfully"
}

# Function to create environment file
create_env_file() {
    echo "📝 Creating environment file..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        
        # Generate random secret key
        SECRET_KEY=$(openssl rand -hex 32)
        sed -i "s/your-secret-key-here/$SECRET_KEY/g" .env
        
        # Set JWT keys
        if [ -f ssl/jwt_private_key.pem ] && [ -f ssl/jwt_public_key.pem ]; then
            PRIVATE_KEY=$(cat ssl/jwt_private_key.pem | tr '\n' '\\n')
            PUBLIC_KEY=$(cat ssl/jwt_public_key.pem | tr '\n' '\\n')
            
            sed -i "s|-----BEGIN PRIVATE KEY-----.*-----END PRIVATE KEY-----|$PRIVATE_KEY|g" .env
            sed -i "s|-----BEGIN PUBLIC KEY-----.*-----END PUBLIC KEY-----|$PUBLIC_KEY|g" .env
        fi
        
        echo "✅ Environment file created"
    else
        echo "ℹ️  Environment file already exists"
    fi
}

# Function to build and start services
deploy_services() {
    echo "🐳 Building and starting Docker services..."
    
    if [ "$ENVIRONMENT" = "prod" ]; then
        # Production deployment
        docker-compose -f docker-compose.prod.yml down
        docker-compose -f docker-compose.prod.yml build --no-cache
        docker-compose -f docker-compose.prod.yml up -d
        
        echo "🌐 Production services started:"
        echo "   - API: https://localhost (with SSL)"
        echo "   - Health: https://localhost/health"
        echo "   - Docs: https://localhost/docs (if debug enabled)"
    else
        # Development deployment
        docker-compose down
        docker-compose build
        docker-compose up -d
        
        echo "🌐 Development services started:"
        echo "   - API: http://localhost:8000"
        echo "   - Health: http://localhost:8000/health"
        echo "   - Docs: http://localhost:8000/docs"
        echo "   - Redis: localhost:6379"
    fi
}

# Function to show service status
show_status() {
    echo "📊 Service Status:"
    
    if [ "$ENVIRONMENT" = "prod" ]; then
        docker-compose -f docker-compose.prod.yml ps
    else
        docker-compose ps
    fi
}

# Function to show logs
show_logs() {
    echo "📋 Recent logs:"
    
    if [ "$ENVIRONMENT" = "prod" ]; then
        docker-compose -f docker-compose.prod.yml logs --tail=20
    else
        docker-compose logs --tail=20
    fi
}

# Main deployment flow
main() {
    case $ENVIRONMENT in
        "dev")
            echo "🔧 Development deployment"
            create_env_file
            deploy_services
            ;;
        "prod")
            echo "🏭 Production deployment"
            generate_jwt_keys
            generate_ssl_certs
            create_env_file
            deploy_services
            ;;
        "status")
            show_status
            exit 0
            ;;
        "logs")
            show_logs
            exit 0
            ;;
        "stop")
            echo "🛑 Stopping services..."
            docker-compose down
            docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
            echo "✅ Services stopped"
            exit 0
            ;;
        *)
            echo "❌ Invalid environment. Use: dev, prod, status, logs, or stop"
            exit 1
            ;;
    esac
    
    echo ""
    show_status
    echo ""
    echo "✅ Deployment completed successfully!"
    echo ""
    echo "📚 Useful commands:"
    echo "   ./deploy.sh status  - Show service status"
    echo "   ./deploy.sh logs    - Show recent logs"
    echo "   ./deploy.sh stop    - Stop all services"
    
    if [ "$ENVIRONMENT" = "dev" ]; then
        echo "   docker-compose logs -f sso-api  - Follow API logs"
    else
        echo "   docker-compose -f docker-compose.prod.yml logs -f sso-api  - Follow API logs"
    fi
}

# Run main function
main