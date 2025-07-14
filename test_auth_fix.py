import sys
import logging
import requests
import json
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the app directory to the path so we can import modules
sys.path.append(".")

def get_auth_token() -> str:
    """Get an authentication token for API requests"""
    from app.core.security import create_access_token
    
    # Create a token for a test user (or admin)
    # This bypasses the need to make an actual login request
    user_id = "12345678-1234-5678-1234-567812345678"  # Use a valid user ID
    token = create_access_token(user_id)
    return token

def test_branches_endpoint():
    """Test the branches endpoint directly"""
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
        # Use the local server if it's running, or start one if needed
        url = "http://localhost:8000/api/v1/admin/branches"
        logger.info(f"Making request to: {url}")
        
        response = requests.get(url, headers=headers)
        
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

def fix_branch_response():
    """Apply a fix to the BranchResponse schema"""
    from app.schemas.organization import BranchResponse
    from app.models.branch import Branch
    from app.core.database import SessionLocal
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Get a branch from the database
        branch = db.query(Branch).first()
        
        if not branch:
            logger.error("No branches found in the database")
            return
        
        # Log the branch details
        logger.info(f"Branch ID: {branch.id}, Type: {type(branch.id)}")
        
        # Test the fix: manually convert the branch to a response
        branch_dict = {
            "id": str(branch.id),  # Explicitly convert UUID to string
            "branch_name": branch.branch_name,
            "branch_code": branch.branch_code,
            "address": branch.address,
            "province": branch.province
        }
        
        # Create a BranchResponse directly from the dictionary
        response = BranchResponse(**branch_dict)
        logger.info(f"Manual conversion successful: {response}")
        
        # Propose a fix for the endpoint
        logger.info("\nProposed fix for the endpoint in app/api/admin.py:")
        logger.info("""
        @router.get("/branches", response_model=List[BranchResponse])
        async def get_all_branches(
            current_user: User = Depends(require_auth),
            db: Session = Depends(get_db)
        ):
            admin_service = AdminService(db)
            admin_service.verify_admin_access(str(current_user.id))
            
            branches = db.query(Branch).all()
            
            # Manual conversion to ensure UUID is properly converted to string
            return [
                BranchResponse(
                    id=str(branch.id),
                    branch_name=branch.branch_name,
                    branch_code=branch.branch_code,
                    address=branch.address,
                    province=branch.province
                ) for branch in branches
            ]
        """)
        
    finally:
        db.close()

if __name__ == "__main__":
    # Uncomment to test the endpoint (requires the API server to be running)
    # test_branches_endpoint()
    
    # Apply and test the fix
    fix_branch_response()
