import sys
import logging
import uuid
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

def create_test_branch():
    """Create a test branch and test the conversion to BranchResponse"""
    # Create a database session
    db = SessionLocal()
    
    try:
        # Create a test branch with a known UUID
        test_id = uuid.UUID('12345678-1234-5678-1234-567812345678')
        
        # Check if the branch already exists
        existing = db.query(Branch).filter(Branch.id == test_id).first()
        if existing:
            logger.info(f"Test branch already exists with ID: {test_id}")
            branch = existing
        else:
            # Create a new test branch
            branch = Branch(
                id=test_id,
                branch_name="Test Branch",
                branch_code="TEST123",
                address="123 Test Street",
                province="Test Province"
            )
            db.add(branch)
            db.commit()
            db.refresh(branch)
            logger.info(f"Created test branch with ID: {branch.id}")
        
        # Log the branch details
        logger.info(f"Branch ID: {branch.id}, Type: {type(branch.id)}")
        logger.info(f"Branch Name: {branch.branch_name}")
        
        # Try to convert using model_validate
        try:
            logger.info("Attempting to convert using model_validate...")
            response = BranchResponse.model_validate(branch)
            logger.info(f"Success! Response: {response}")
            logger.info(f"Response ID type: {type(response.id)}, value: {response.id}")
        except Exception as e:
            logger.error(f"model_validate conversion failed: {str(e)}")
            
            # Add debug information about the branch object
            logger.debug(f"Branch __dict__: {branch.__dict__}")
            
            # Try with manual conversion
            try:
                logger.info("Attempting manual conversion...")
                branch_dict = {
                    "id": str(branch.id),
                    "branch_name": branch.branch_name,
                    "branch_code": branch.branch_code,
                    "address": branch.address,
                    "province": branch.province
                }
                response = BranchResponse(**branch_dict)
                logger.info(f"Manual conversion successful: {response}")
            except Exception as e2:
                logger.error(f"Manual conversion failed: {str(e2)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    create_test_branch()
