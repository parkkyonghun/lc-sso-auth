import sys
import logging
import requests
import json
import subprocess
import time
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the app directory to the path so we can import modules
sys.path.append(".")

def start_api_server():
    """Start the FastAPI server in a separate process"""
    logger.info("Starting FastAPI server...")
    # Use uvicorn to start the server
    process = subprocess.Popen(
        ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for the server to start
    time.sleep(3)
    return process

def stop_api_server(process):
    """Stop the FastAPI server"""
    logger.info("Stopping FastAPI server...")
    process.terminate()
    process.wait()

def get_auth_token() -> str:
    """Get an authentication token for API requests"""
    logger.info("Getting authentication token...")
    
    # This is a simplified example - in a real scenario, you'd use actual credentials
    auth_data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post("http://127.0.0.1:8000/api/v1/auth/login", json=auth_data)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token", "")
    except Exception as e:
        logger.error(f"Failed to get auth token: {str(e)}")
        return ""

def test_branches_endpoint():
    """Test the branches endpoint"""
    logger.info("Testing branches endpoint...")
    
    # Get auth token
    token = get_auth_token()
    if not token:
        logger.error("No auth token available, cannot test endpoint")
        return
    
    # Set up headers with auth token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Make request to branches endpoint
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/admin/branches", headers=headers)
        
        # Log response status and headers
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        
        # Try to parse response as JSON
        try:
            data = response.json()
            logger.info(f"Response data: {json.dumps(data, indent=2)}")
        except Exception as e:
            logger.error(f"Failed to parse response as JSON: {str(e)}")
            logger.info(f"Response text: {response.text}")
    
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")

def main():
    """Main function to run the tests"""
    # Start the API server
    server_process = start_api_server()
    
    try:
        # Test the branches endpoint
        test_branches_endpoint()
    finally:
        # Stop the API server
        stop_api_server(server_process)

if __name__ == "__main__":
    main()
