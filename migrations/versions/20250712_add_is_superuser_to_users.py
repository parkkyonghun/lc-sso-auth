"""Add is_superuser field to users table

Revision ID: add_is_superuser
Revises: 
Create Date: 2025-07-12 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_is_superuser'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Add is_superuser column to users table."""
    op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade():
    """Drop is_superuser column from users table."""
    op.drop_column('users', 'is_superuser')
