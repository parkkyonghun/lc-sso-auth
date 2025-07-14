@echo off
REM Flask Admin Docker Deployment Script for Windows
REM This script helps deploy the Flask Admin application using Docker

setlocal enabledelayedexpansion

echo ========================================
echo Flask Admin Docker Deployment
echo ========================================
echo.

if "%1"=="" (
    echo Usage: docker-deploy.bat [command]
    echo.
    echo Available commands:
    echo   start     - Start Flask Admin services
    echo   stop      - Stop Flask Admin services
    echo   restart   - Restart Flask Admin services
    echo   logs      - View Flask Admin logs
    echo   status    - Check service status
    echo   build     - Build Flask Admin image
    echo   clean     - Clean up Docker resources
    echo   help      - Show this help message
    echo.
    goto :end
)

set COMMAND=%1

if "%COMMAND%"=="start" (
    echo Starting Flask Admin services...
    docker-compose up -d
    if !errorlevel! equ 0 (
        echo.
        echo ✅ Flask Admin services started successfully!
        echo.
        echo 🌐 Flask Admin UI: http://localhost:5000
        echo 📊 Redis: localhost:6381
        echo.
        echo Use 'docker-deploy.bat logs' to view logs
        echo Use 'docker-deploy.bat status' to check status
    ) else (
        echo ❌ Failed to start Flask Admin services
    )
    goto :end
)

if "%COMMAND%"=="stop" (
    echo Stopping Flask Admin services...
    docker-compose down
    if !errorlevel! equ 0 (
        echo ✅ Flask Admin services stopped successfully!
    ) else (
        echo ❌ Failed to stop Flask Admin services
    )
    goto :end
)

if "%COMMAND%"=="restart" (
    echo Restarting Flask Admin services...
    docker-compose down
    docker-compose up -d
    if !errorlevel! equ 0 (
        echo ✅ Flask Admin services restarted successfully!
        echo 🌐 Flask Admin UI: http://localhost:5000
    ) else (
        echo ❌ Failed to restart Flask Admin services
    )
    goto :end
)

if "%COMMAND%"=="logs" (
    echo Showing Flask Admin logs...
    docker-compose logs -f flask-admin
    goto :end
)

if "%COMMAND%"=="status" (
    echo Checking Flask Admin service status...
    docker-compose ps
    goto :end
)

if "%COMMAND%"=="build" (
    echo Building Flask Admin image...
    docker-compose build --no-cache
    if !errorlevel! equ 0 (
        echo ✅ Flask Admin image built successfully!
    ) else (
        echo ❌ Failed to build Flask Admin image
    )
    goto :end
)

if "%COMMAND%"=="clean" (
    echo Cleaning up Flask Admin Docker resources...
    docker-compose down -v
    docker system prune -f
    echo ✅ Flask Admin Docker resources cleaned up!
    goto :end
)

if "%COMMAND%"=="help" (
    echo Flask Admin Docker Deployment Commands:
    echo.
    echo   start     - Start Flask Admin services
    echo   stop      - Stop Flask Admin services  
    echo   restart   - Restart Flask Admin services
    echo   logs      - View Flask Admin logs
    echo   status    - Check service status
    echo   build     - Build Flask Admin image
    echo   clean     - Clean up Docker resources
    echo   help      - Show this help message
    echo.
    goto :end
)

echo ❌ Unknown command: %COMMAND%
echo Use 'docker-deploy.bat help' for available commands

:end
endlocal