import sys
import logging
from typing import List
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the app directory to the path so we can import modules
sys.path.append(".")

# Import the necessary modules
from app.models.branch import Branch
from app.schemas.organization import BranchResponse
from app.core.database import SessionLocal

def test_get_all_branches():
    """Test the exact behavior of the get_all_branches endpoint"""
    # Create a database session
    db = SessionLocal()
    
    try:
        # Get all branches (exactly like the endpoint does)
        logger.info("Querying all branches...")
        branches = db.query(Branch).all()
        logger.info(f"Found {len(branches)} branches")
        
        # Log the first branch details for reference
        if branches:
            branch = branches[0]
            logger.info(f"First branch - ID: {branch.id}, Type: {type(branch.id)}")
            logger.info(f"First branch - Name: {branch.branch_name}")
        
        # Try to convert all branches using model_validate (like the endpoint does)
        try:
            logger.info("Attempting to convert all branches using model_validate...")
            responses = [BranchResponse.model_validate(branch) for branch in branches]
            logger.info(f"Success! Converted {len(responses)} branches")
            
            # Log the first response for verification
            if responses:
                logger.info(f"First response - ID: {responses[0].id}, Type: {type(responses[0].id)}")
                logger.info(f"First response - Name: {responses[0].branch_name}")
        except Exception as e:
            logger.error(f"model_validate conversion failed: {str(e)}")
            
            # Try with manual conversion as a fallback
            try:
                logger.info("Attempting manual conversion as fallback...")
                responses = []
                for branch in branches:
                    branch_dict = {
                        "id": str(branch.id),
                        "branch_name": branch.branch_name,
                        "branch_code": branch.branch_code,
                        "address": branch.address,
                        "province": branch.province
                    }
                    response = BranchResponse(**branch_dict)
                    responses.append(response)
                logger.info(f"Manual conversion successful for {len(responses)} branches")
            except Exception as e2:
                logger.error(f"Manual conversion also failed: {str(e2)}")
        
        # Test the exact line from the endpoint
        try:
            logger.info("Testing exact endpoint code...")
            result = [BranchResponse.model_validate(branch) for branch in branches]
            logger.info(f"Endpoint code works! Converted {len(result)} branches")
        except Exception as e:
            logger.error(f"Endpoint code failed: {str(e)}")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_get_all_branches()
