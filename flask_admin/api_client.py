"""
API Client for communicating with FastAPI backend
"""

import requests
from typing import Dict, Any, Optional
from config import Config


class FastAPIClient:
    """Client for FastAPI communication"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def set_auth_token(self, token: str):
        """Set JWT token for authentication"""
        self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def clear_auth_token(self):
        """Clear JWT token"""
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate with FastAPI backend"""
        try:
            response = self.session.post(
                f'{self.base_url}/auth/login',
                data={'username': username, 'password': password},
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'accept': 'application/json'
                }
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': 'Invalid credentials'}
        except Exception as e:
            return {'error': f'Connection error: {str(e)}'}
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to API"""
        try:
            response = self.session.get(f'{self.base_url}{endpoint}', params=params)
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'API Error: {response.status_code}', 'status_code': response.status_code}
        except Exception as e:
            return {'error': f'Connection error: {str(e)}'}
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to API"""
        try:
            response = self.session.post(
                f'{self.base_url}{endpoint}',
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {'error': f'API Error: {response.status_code}', 'status_code': response.status_code}
        except Exception as e:
            return {'error': f'Connection error: {str(e)}'}
    
    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make PUT request to API"""
        try:
            response = self.session.put(
                f'{self.base_url}{endpoint}',
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'API Error: {response.status_code}', 'status_code': response.status_code}
        except Exception as e:
            return {'error': f'Connection error: {str(e)}'}
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request to API"""
        try:
            response = self.session.delete(f'{self.base_url}{endpoint}')
            if response.status_code in [200, 204]:
                if response.content:
                    return response.json()
                else:
                    return {'success': True}
            else:
                return {'error': f'API Error: {response.status_code}', 'status_code': response.status_code}
        except Exception as e:
            return {'error': f'Connection error: {str(e)}'}


# Global API client instance
api_client = FastAPIClient(Config.FASTAPI_BASE_URL)


# Helper functions for API data
def get_branches():
    """Get branches from API"""
    result = api_client.get('/api/v1/admin/branches')
    if 'error' in result:
        return []
    return result


def get_departments():
    """Get departments from API"""
    result = api_client.get('/api/v1/admin/departments')
    if 'error' in result:
        return []
    return result


def get_positions():
    """Get positions from API"""
    result = api_client.get('/api/v1/admin/positions')
    if 'error' in result:
        return []
    return result


def handle_api_error(result: Dict[str, Any], error_message: str = "API Error") -> bool:
    """
    Handle API errors consistently across the application.
    Returns True if there was an error, False otherwise.
    """
    if 'error' in result:
        from flask import flash
        flash(f"{error_message}: {result['error']}", 'danger')
        return True
    return False
