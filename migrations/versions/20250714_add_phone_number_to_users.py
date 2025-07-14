"""Add phone_number field to users table

Revision ID: add_phone_number
Revises: add_is_superuser
Create Date: 2025-07-14 18:06:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_phone_number'
down_revision = 'add_is_superuser'
branch_labels = None
depends_on = None

def upgrade():
    """Add phone_number column to users table."""
    op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))

def downgrade():
    """Drop phone_number column from users table."""
    op.drop_column('users', 'phone_number')