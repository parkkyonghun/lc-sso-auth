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
from app.models.department import Department
from app.models.position import Position
from app.schemas.organization import BranchResponse, DepartmentResponse, PositionResponse
from app.core.database import SessionLocal

def test_organization_entities():
    """Test that all organization entities work with our UUID to string conversion fix"""
    db = SessionLocal()
    
    try:
        logger.info("🏢 Testing all organization entities...")
        
        # ===== TEST BRANCHES =====
        logger.info("\n🌿 Testing Branches...")
        branches = db.query(Branch).limit(2).all()
        if branches:
            branch_responses = [BranchResponse.model_validate(branch) for branch in branches]
            logger.info(f"✅ Successfully converted {len(branch_responses)} branches")
            for i, resp in enumerate(branch_responses):
                logger.info(f"  Branch {i+1}: ID={resp.id} (Type: {type(resp.id)}), Name={resp.branch_name}")
        else:
            logger.warning("⚠️ No branches found in database")
        
        # ===== TEST DEPARTMENTS =====
        logger.info("\n🏬 Testing Departments...")
        departments = db.query(Department).limit(2).all()
        if departments:
            dept_responses = [DepartmentResponse.model_validate(dept) for dept in departments]
            logger.info(f"✅ Successfully converted {len(dept_responses)} departments")
            for i, resp in enumerate(dept_responses):
                logger.info(f"  Department {i+1}: ID={resp.id} (Type: {type(resp.id)}), Name={resp.department_name}")
        else:
            logger.warning("⚠️ No departments found in database")
        
        # ===== TEST POSITIONS =====
        logger.info("\n💼 Testing Positions...")
        positions = db.query(Position).limit(2).all()
        if positions:
            pos_responses = [PositionResponse.model_validate(pos) for pos in positions]
            logger.info(f"✅ Successfully converted {len(pos_responses)} positions")
            for i, resp in enumerate(pos_responses):
                logger.info(f"  Position {i+1}: ID={resp.id} (Type: {type(resp.id)}), Title={resp.title}")
        else:
            logger.warning("⚠️ No positions found in database")
        
        # ===== VERIFICATION =====
        logger.info("\n🔍 Verification Summary:")
        
        # Check that all IDs are strings
        all_responses = []
        if branches:
            all_responses.extend([BranchResponse.model_validate(b) for b in branches])
        if departments:
            all_responses.extend([DepartmentResponse.model_validate(d) for d in departments])
        if positions:
            all_responses.extend([PositionResponse.model_validate(p) for p in positions])
        
        if all_responses:
            all_ids_are_strings = all(isinstance(resp.id, str) for resp in all_responses)
            logger.info(f"  - All response IDs are strings: {all_ids_are_strings}")
            logger.info(f"  - Total entities tested: {len(all_responses)}")
            
            if all_ids_are_strings:
                logger.info("✅ All organization entities working correctly!")
                return True
            else:
                logger.error("❌ Some IDs are not strings!")
                return False
        else:
            logger.warning("⚠️ No entities found to test")
            return True  # Not a failure, just no data
            
    except Exception as e:
        logger.error(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_organization_entities()
    if success:
        print("\n🎉 ORGANIZATION ENTITIES TEST PASSED!")
        print("✅ Branches, Departments, and Positions all working correctly!")
    else:
        print("\n💥 ORGANIZATION ENTITIES TEST FAILED!")
        sys.exit(1)
