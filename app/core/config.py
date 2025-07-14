from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application
    app_name: str = "SSO Service"
    app_description: str = "FastAPI SSO and OAuth 2.0 Service"
    app_version: str = "1.0.0"
    debug: bool = False
    secret_key: str = "your-secret-key-here"
    
    # Database
    database_url: str = "postgresql://postgres:123456@localhost:5432/ssodb"
    
    # Cache
    cache_url: str = "redis://localhost:6379"
    
    # JWT Configuration
    jwt_algorithm: str = "RS256"
    jwt_private_key: str = ""
    jwt_public_key: str = ""
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 30
    jwt_id_token_expire_minutes: int = 60
    
    # CORS Settings
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    allowed_hosts: List[str] = []
    
    # Session Configuration
    session_expire_minutes: int = 60
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    
    # Email Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = "your-email@gmail.com"
    smtp_password: str = "your-app-password"
    smtp_from_email: str = "your-email@gmail.com"
    smtp_from_name: str = "FastAPI SSO"
    
    # OAuth Configuration
    oauth_authorization_code_expire_minutes: int = 10
    oauth_refresh_token_expire_days: int = 30
    
    # Security Settings
    password_min_length: int = 8
    max_login_attempts: int = 5
    account_lockout_duration_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.allowed_hosts:
            self.allowed_hosts = ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
        # Load RSA keys from files
        import os
        # Get the absolute path to the project's root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        private_key_path = os.path.join(project_root, "keys", "private_key.pem")
        public_key_path = os.path.join(project_root, "keys", "public_key.pem")

        try:
            with open(private_key_path, "r") as f:
                self.jwt_private_key = f.read()
            with open(public_key_path, "r") as f:
                self.jwt_public_key = f.read()
        except Exception as e:
            print(f"Warning: Could not load JWT keys: {e}")
            if not self.jwt_private_key or not self.jwt_public_key:
                raise ValueError("JWT keys are required. Please generate them first.")

    class Config:
        env_file = ".env"

settings = Settings()