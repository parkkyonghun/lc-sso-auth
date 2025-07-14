@echo off
REM Docker Deployment Script for FastAPI SSO System
REM This script provides easy deployment options for Windows

setlocal enabledelayedexpansion

echo ========================================
echo   FastAPI SSO System - Docker Deploy
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not available
    echo Please ensure Docker Desktop is running
    pause
    exit /b 1
)

echo ✅ Docker is available
echo.

echo Select deployment option:
echo 1. Development (SQLite + Redis) - Quick start
echo 2. PostgreSQL (PostgreSQL + Redis + pgAdmin) - Full database
echo 3. Production (with Nginx + SSL ready) - Production deployment
echo 4. Stop all services
echo 5. View logs
echo 6. Clean up (remove containers and volumes)
echo.
set /p choice=Enter your choice (1-6): 

if "%choice%"=="1" goto dev
if "%choice%"=="2" goto postgres
if "%choice%"=="3" goto production
if "%choice%"=="4" goto stop
if "%choice%"=="5" goto logs
if "%choice%"=="6" goto cleanup

echo Invalid choice. Please select 1-6.
pause
exit /b 1

:dev
echo.
echo 🚀 Starting Development Environment...
echo Services: FastAPI SSO (8000) + Redis (6379)
echo.
docker-compose up -d
if errorlevel 1 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)
echo.
echo ✅ Development environment started successfully!
echo 🌐 API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 🔧 Admin: Create admin with 'docker-compose exec sso-api python create_admin.py'
echo.
goto end

:postgres
echo.
echo 🐘 Starting PostgreSQL Environment...
echo Services: FastAPI SSO (8000) + PostgreSQL (5432) + Redis (6379) + pgAdmin (5050)
echo.
docker-compose -f docker-compose.postgres.yml up -d
if errorlevel 1 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)
echo.
echo ✅ PostgreSQL environment started successfully!
echo 🌐 API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 🗄️ pgAdmin: http://localhost:5050 (admin@sso.local / admin123)
echo 🔧 Database: localhost:5432 (sso_user / sso_password / sso_db)
echo.
goto end

:production
echo.
echo ⚠️ Production Deployment
echo This requires environment variables to be set.
echo.
set /p confirm=Do you have JWT keys and secrets configured? (y/n): 
if /i not "%confirm%"=="y" (
    echo.
    echo Please configure the following environment variables:
    echo - JWT_PRIVATE_KEY
    echo - JWT_PUBLIC_KEY  
    echo - SECRET_KEY
    echo - REDIS_PASSWORD
    echo.
    echo See DOCKER_DEPLOYMENT_GUIDE.md for details.
    pause
    exit /b 1
)
echo.
echo 🏭 Starting Production Environment...
echo Services: FastAPI SSO (8000) + Redis (6379) + Nginx (80/443)
echo.
docker-compose -f docker-compose.prod.yml up -d
if errorlevel 1 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)
echo.
echo ✅ Production environment started successfully!
echo 🌐 API: http://localhost:8000
echo 🌍 Web: http://localhost (via Nginx)
echo 📚 API Docs: http://localhost:8000/docs
echo.
goto end

:stop
echo.
echo 🛑 Stopping all services...
docker-compose down
docker-compose -f docker-compose.postgres.yml down
docker-compose -f docker-compose.prod.yml down
echo ✅ All services stopped.
echo.
goto end

:logs
echo.
echo Select service to view logs:
echo 1. SSO API
echo 2. Redis
echo 3. PostgreSQL
echo 4. Nginx
echo 5. All services
echo.
set /p logchoice=Enter choice (1-5): 

if "%logchoice%"=="1" docker-compose logs -f sso-api
if "%logchoice%"=="2" docker-compose logs -f redis
if "%logchoice%"=="3" docker-compose -f docker-compose.postgres.yml logs -f postgres
if "%logchoice%"=="4" docker-compose -f docker-compose.prod.yml logs -f nginx
if "%logchoice%"=="5" docker-compose logs -f

goto end

:cleanup
echo.
echo ⚠️ WARNING: This will remove all containers, volumes, and data!
set /p confirm=Are you sure? (y/n): 
if /i not "%confirm%"=="y" (
    echo Cleanup cancelled.
    goto end
)
echo.
echo 🧹 Cleaning up Docker resources...
docker-compose down -v
docker-compose -f docker-compose.postgres.yml down -v
docker-compose -f docker-compose.prod.yml down -v
docker system prune -f
echo ✅ Cleanup completed.
echo.

:end
echo.
echo 📖 For more information, see DOCKER_DEPLOYMENT_GUIDE.md
echo 🆘 Need help? Check logs with option 5 or visit the documentation.
echo.
pause