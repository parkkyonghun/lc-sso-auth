"""Add user profile fields

Revision ID: add_user_profile_fields
Revises: add_is_superuser
Create Date: 2025-01-13 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'add_user_profile_fields'
down_revision = 'add_is_superuser'
branch_labels = None
depends_on = None

def upgrade():
    """Add user profile and organization fields to users table."""
    # Add profile fields
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('timezone', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('language', sa.String(10), nullable=True))
    op.add_column('users', sa.Column('manager_name', sa.String(255), nullable=True))
    
    # Add organization fields
    op.add_column('users', sa.Column('branch_id', UUID(as_uuid=True), nullable=True))
    op.add_column('users', sa.Column('department_id', UUID(as_uuid=True), nullable=True))
    op.add_column('users', sa.Column('position_id', UUID(as_uuid=True), nullable=True))
    
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_users_branch_id', 'users', 'branches',
        ['branch_id'], ['id'], ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_users_department_id', 'users', 'departments',
        ['department_id'], ['id'], ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_users_position_id', 'users', 'positions',
        ['position_id'], ['id'], ondelete='SET NULL'
    )

def downgrade():
    """Remove user profile and organization fields from users table."""
    # Drop foreign key constraints
    op.drop_constraint('fk_users_position_id', 'users', type_='foreignkey')
    op.drop_constraint('fk_users_department_id', 'users', type_='foreignkey')
    op.drop_constraint('fk_users_branch_id', 'users', type_='foreignkey')
    
    # Drop organization fields
    op.drop_column('users', 'position_id')
    op.drop_column('users', 'department_id')
    op.drop_column('users', 'branch_id')
    
    # Drop profile fields
    op.drop_column('users', 'manager_name')
    op.drop_column('users', 'language')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'bio')