#!/usr/bin/env python3
"""
Integrated System Startup Script

This script starts both the FastAPI backend and Flask admin frontend
in the correct order and monitors their health.
"""

import subprocess
import time
import sys
import os
import signal
import requests
from pathlib import Path

class IntegratedSystemManager:
    def __init__(self):
        self.fastapi_process = None
        self.flask_process = None
        self.project_root = Path(__file__).parent
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        # Replace emoji characters with text alternatives to avoid encoding issues
        message = message.replace("🚀", "[ROCKET]")
        message = message.replace("✅", "[OK]")
        message = message.replace("❌", "[ERROR]")
        message = message.replace("🛑", "[STOP]")
        message = message.replace("👀", "[MONITORING]")
        message = message.replace("🎉", "[SUCCESS]")
        message = message.replace("📋", "[INFO]")
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def check_port(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def wait_for_service(self, port: int, service_name: str, max_wait: int = 30) -> bool:
        """Wait for a service to become available"""
        self.log(f"Waiting for {service_name} on port {port}...")
        
        for i in range(max_wait):
            if self.check_port(port):
                self.log(f"✅ {service_name} is ready on port {port}")
                return True
            time.sleep(1)
        
        self.log(f"❌ {service_name} failed to start within {max_wait} seconds", "ERROR")
        return False
    
    def start_fastapi(self) -> bool:
        """Start FastAPI backend"""
        self.log("🚀 Starting FastAPI backend...")
        
        try:
            # Change to project root directory
            os.chdir(self.project_root)
            
            # Start FastAPI with uvicorn
            cmd = [
                sys.executable, "-m", "uvicorn",
                "app.main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ]
            
            self.fastapi_process = subprocess.Popen(
                cmd,
                text=True
            )
            
            # Wait for FastAPI to start
            if self.wait_for_service(8000, "FastAPI Backend"):
                return True
            else:
                self.stop_fastapi()
                return False
                
        except Exception as e:
            self.log(f"❌ Failed to start FastAPI: {e}", "ERROR")
            return False
    
    def start_flask(self) -> bool:
        """Start Flask admin frontend"""
        self.log("🚀 Starting Flask admin frontend...")
        
        try:
            # Change to flask_admin directory
            flask_dir = self.project_root / "flask_admin"
            os.chdir(flask_dir)
            
            # Start Flask
            cmd = [sys.executable, "main_app.py"]
            
            self.flask_process = subprocess.Popen(
                cmd,
                text=True,
                env={**os.environ, "FLASK_ENV": "development"}
            )
            
            # Wait for Flask to start
            if self.wait_for_service(5000, "Flask Admin"):
                return True
            else:
                self.stop_flask()
                return False
                
        except Exception as e:
            self.log(f"❌ Failed to start Flask: {e}", "ERROR")
            return False
    
    def stop_fastapi(self):
        """Stop FastAPI backend"""
        if self.fastapi_process:
            self.log("🛑 Stopping FastAPI backend...")
            self.fastapi_process.terminate()
            try:
                self.fastapi_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.fastapi_process.kill()
            self.fastapi_process = None
    
    def stop_flask(self):
        """Stop Flask admin frontend"""
        if self.flask_process:
            self.log("🛑 Stopping Flask admin...")
            self.flask_process.terminate()
            try:
                self.flask_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.flask_process.kill()
            self.flask_process = None
    
    def stop_all(self):
        """Stop all services"""
        self.stop_flask()
        self.stop_fastapi()
    
    def monitor_services(self):
        """Monitor services and restart if needed"""
        self.log("👀 Monitoring services...")
        
        try:
            while True:
                # Check FastAPI
                if not self.check_port(8000):
                    self.log("❌ FastAPI backend is down, restarting...", "WARNING")
                    self.stop_fastapi()
                    if not self.start_fastapi():
                        break
                
                # Check Flask
                if not self.check_port(5000):
                    self.log("❌ Flask admin is down, restarting...", "WARNING")
                    self.stop_flask()
                    if not self.start_flask():
                        break
                
                time.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            self.log("🛑 Received interrupt signal, shutting down...")
        except Exception as e:
            self.log(f"❌ Monitor error: {e}", "ERROR")
    
    def run(self):
        """Run the integrated system"""
        self.log("🚀 Starting Integrated SSO System...")
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            self.log("🛑 Received shutdown signal")
            self.stop_all()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Start FastAPI first
            if not self.start_fastapi():
                self.log("❌ Failed to start FastAPI backend", "ERROR")
                return False
            
            # Start Flask admin
            if not self.start_flask():
                self.log("❌ Failed to start Flask admin", "ERROR")
                self.stop_fastapi()
                return False
            
            # Display success message
            self.log("🎉 Integrated system started successfully!")
            self.log("📋 Access points:")
            self.log("   - FastAPI Backend: http://localhost:8000")
            self.log("   - FastAPI Docs: http://localhost:8000/docs")
            self.log("   - Flask Admin: http://localhost:5000")
            self.log("   - Health Check: http://localhost:8000/health")

            # Monitor services to keep the script running
            self.monitor_services()
            self.log("")
            self.log("Press Ctrl+C to stop all services")
            
            # Monitor services
            self.monitor_services()
            
            return True
            
        except Exception as e:
            self.log(f"❌ System startup failed: {e}", "ERROR")
            self.stop_all()
            return False
        finally:
            self.stop_all()

def main():
    """Main function"""
    print("=" * 60)
    print("Flask Admin + FastAPI Backend Integrated System")
    print("=" * 60)
    
    manager = IntegratedSystemManager()
    success = manager.run()
    
    if not success:
        print("\n❌ System startup failed. Check the logs above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
