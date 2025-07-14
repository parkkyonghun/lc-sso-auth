@echo off
setlocal enabledelayedexpansion

REM SSO Service Deployment Script for Windows
REM Usage: deploy.bat [dev|prod|status|logs|stop]

set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=dev
set PROJECT_NAME=sso-service

echo 🚀 Deploying SSO Service in %ENVIRONMENT% mode...

if "%ENVIRONMENT%"=="dev" goto :deploy_dev
if "%ENVIRONMENT%"=="prod" goto :deploy_prod
if "%ENVIRONMENT%"=="status" goto :show_status
if "%ENVIRONMENT%"=="logs" goto :show_logs
if "%ENVIRONMENT%"=="stop" goto :stop_services

echo ❌ Invalid environment. Use: dev, prod, status, logs, or stop
exit /b 1

:deploy_dev
echo 🔧 Development deployment
call :create_env_file
call :deploy_dev_services
goto :show_final_status

:deploy_prod
echo 🏭 Production deployment
echo ⚠️  For production deployment on Windows, please:
echo    1. Install OpenSSL (https://slproweb.com/products/Win32OpenSSL.html)
echo    2. Generate JWT keys manually:
echo       openssl genrsa -out ssl\jwt_private_key.pem 2048
echo       openssl rsa -in ssl\jwt_private_key.pem -pubout -out ssl\jwt_public_key.pem
echo    3. Generate SSL certificates:
echo       openssl req -x509 -newkey rsa:4096 -keyout ssl\key.pem -out ssl\cert.pem -days 365 -nodes
echo    4. Update .env file with generated keys
echo.
call :create_env_file
call :deploy_prod_services
goto :show_final_status

:create_env_file
echo 📝 Creating environment file...
if not exist .env (
    copy .env.example .env
    echo ✅ Environment file created from example
) else (
    echo ℹ️  Environment file already exists
)
exit /b 0

:deploy_dev_services
echo 🐳 Building and starting Docker services for development...
docker-compose down
docker-compose build
docker-compose up -d

echo 🌐 Development services started:
echo    - API: http://localhost:8000
echo    - Health: http://localhost:8000/health
echo    - Docs: http://localhost:8000/docs
echo    - Redis: localhost:6379
exit /b 0

:deploy_prod_services
echo 🐳 Building and starting Docker services for production...
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

echo 🌐 Production services started:
echo    - API: https://localhost (with SSL)
echo    - Health: https://localhost/health
echo    - Docs: https://localhost/docs (if debug enabled)
exit /b 0

:show_status
echo 📊 Service Status:
if "%ENVIRONMENT%"=="prod" (
    docker-compose -f docker-compose.prod.yml ps
) else (
    docker-compose ps
)
exit /b 0

:show_logs
echo 📋 Recent logs:
if "%ENVIRONMENT%"=="prod" (
    docker-compose -f docker-compose.prod.yml logs --tail=20
) else (
    docker-compose logs --tail=20
)
exit /b 0

:stop_services
echo 🛑 Stopping services...
docker-compose down
docker-compose -f docker-compose.prod.yml down 2>nul
echo ✅ Services stopped
exit /b 0

:show_final_status
echo.
call :show_status
echo.
echo ✅ Deployment completed successfully!
echo.
echo 📚 Useful commands:
echo    deploy.bat status  - Show service status
echo    deploy.bat logs    - Show recent logs
echo    deploy.bat stop    - Stop all services

if "%ENVIRONMENT%"=="dev" (
    echo    docker-compose logs -f sso-api  - Follow API logs
) else (
    echo    docker-compose -f docker-compose.prod.yml logs -f sso-api  - Follow API logs
)
exit /b 0