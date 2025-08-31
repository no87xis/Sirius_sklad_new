"""Fix payment_method values to match enum

Revision ID: 002
Revises: 001
Create Date: 2025-08-28 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Исправляем значения payment_method с 'unpaid' на 'UNPAID'
    op.execute("UPDATE orders SET payment_method = 'UNPAID' WHERE payment_method = 'unpaid'")


def downgrade() -> None:
    # Возвращаем значения payment_method с 'UNPAID' на 'unpaid'
    op.execute("UPDATE orders SET payment_method = 'unpaid' WHERE payment_method = 'UNPAID'")
