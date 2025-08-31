"""add_ordered_not_paid_status_and_nullable_reserved_until

Revision ID: a140102d6876
Revises: 009
Create Date: 2025-08-30 03:19:41.703099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a140102d6876'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Добавляем новый статус и делаем поле reserved_until nullable"""
    # Делаем поле reserved_until nullable
    with op.batch_alter_table('shop_orders') as batch_op:
        batch_op.alter_column('reserved_until', nullable=True)


def downgrade() -> None:
    """Возвращаем поле reserved_until как NOT NULL"""
    # Возвращаем поле reserved_until как NOT NULL
    with op.batch_alter_table('shop_orders') as batch_op:
        batch_op.alter_column('reserved_until', nullable=False)
