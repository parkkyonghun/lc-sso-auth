"""Merge permission_category and user_profile branches

Revision ID: d146748c7f24
Revises: add_user_profile_fields, add_permission_category
Create Date: 2025-07-14 17:48:41.266206

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd146748c7f24'
down_revision = ('add_user_profile_fields', 'add_permission_category')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass