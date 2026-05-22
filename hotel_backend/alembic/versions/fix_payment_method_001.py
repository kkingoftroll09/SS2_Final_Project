"""Fix payment_method column

Revision ID: fix_payment_method_001
Revises: 34bc41bf8ffb
Create Date: 2026-05-15 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'fix_payment_method_001'
down_revision: Union[str, Sequence[str], None] = '34bc41bf8ffb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - ensure payment_method is VARCHAR(100)."""
    # Drop the existing column if it's still ENUM and recreate as VARCHAR
    try:
        op.execute('ALTER TABLE payment MODIFY COLUMN payment_method VARCHAR(100) NULL')
    except Exception as e:
        # If it's already VARCHAR, no harm done
        pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('ALTER TABLE payment MODIFY COLUMN payment_method VARCHAR(50) NULL')
