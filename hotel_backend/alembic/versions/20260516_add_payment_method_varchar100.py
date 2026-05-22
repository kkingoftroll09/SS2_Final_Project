"""add payment_method varchar(100)

Revision ID: 20260516_add_payment_method_varchar100
Revises: 34bc41bf8ffb_sync_db
Create Date: 2026-05-16 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260516_add_payment_method_varchar100'
down_revision = '34bc41bf8ffb_sync_db'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('payment', 'payment_method', existing_type=sa.String(length=50), type_=sa.String(length=100), existing_nullable=True)


def downgrade():
    op.alter_column('payment', 'payment_method', existing_type=sa.String(length=100), type_=sa.String(length=50), existing_nullable=True)
