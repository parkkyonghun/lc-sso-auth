"""Add category column to permissions and rename action_name to permission_name

Revision ID: add_permission_category
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_permission_category'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Rename action_name column to permission_name in permissions table
    op.alter_column('permissions', 'action_name', new_column_name='permission_name')
    
    # Add category column to permissions table
    op.add_column('permissions', sa.Column('category', sa.String(100), nullable=True))
    
    # Update existing permissions to have categories
    connection = op.get_bind()
    
    # Update existing permissions with categories
    connection.execute(
        "UPDATE permissions SET category = 'User Management' WHERE permission_name IN ('create_user', 'delete_user')"
    )


def downgrade():
    # Remove category column
    op.drop_column('permissions', 'category')
    
    # Rename permission_name back to action_name
    op.alter_column('permissions', 'permission_name', new_column_name='action_name')