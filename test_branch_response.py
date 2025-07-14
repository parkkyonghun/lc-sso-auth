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

def test_branch_response():
    """Test the conversion from Branch model to BranchResponse schema"""
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
        logger.info(f"Branch Code: {branch.branch_code}")
        
        # Try to convert using model_validate (this should now work with our fix)
        try:
            logger.info("Attempting to convert using model_validate...")
            response = BranchResponse.model_validate(branch)
            logger.info(f"Success! Response: {response}")
            logger.info(f"Response ID type: {type(response.id)}, value: {response.id}")
        except Exception as e:
            logger.error(f"model_validate conversion failed: {str(e)}")

        # Try manual conversion (for comparison)
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

        # Test with a list of branches (like the endpoint does)
        try:
            logger.info("Testing with multiple branches...")
            branches = db.query(Branch).limit(3).all()
            responses = [BranchResponse.model_validate(branch) for branch in branches]
            logger.info(f"Successfully converted {len(responses)} branches")
            for i, resp in enumerate(responses):
                logger.info(f"Branch {i+1}: ID={resp.id}, Name={resp.branch_name}")
        except Exception as e:
            logger.error(f"Multiple branches conversion failed: {str(e)}")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_branch_response()