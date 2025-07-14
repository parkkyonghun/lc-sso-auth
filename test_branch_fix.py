import sys
import logging
from sqlalchemy.orm import Session
from uuid import UUID

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the app directory to the path so we can import modules
sys.path.append(".")

# Import the necessary modules
from app.models.branch import Branch
from app.schemas.organization import BranchResponse
from app.core.database import SessionLocal

def test_branch_issue():
    """Test the issue with Branch to BranchResponse conversion"""
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
        logger.info(f"Branch Name: {branch.branch_name}")
        
        # Try to convert using model_validate (this will fail)
        try:
            logger.info("Attempting to convert using model_validate...")
            response = BranchResponse.model_validate(branch)
            logger.info(f"Success! Response: {response}")
        except Exception as e:
            logger.error(f"model_validate conversion failed: {str(e)}")
            
        # Try manual conversion (this should work)
        try:
            logger.info("Attempting manual conversion...")
            branch_dict = {
                "id": str(branch.id),  # Convert UUID to string
                "branch_name": branch.branch_name,
                "branch_code": branch.branch_code,
                "address": branch.address,
                "province": branch.province
            }
            response = BranchResponse(**branch_dict)
            logger.info(f"Manual conversion successful: {response}")
        except Exception as e:
            logger.error(f"Manual conversion failed: {str(e)}")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_branch_issue()