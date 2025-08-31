"""Add source field to orders table for shop integration

Revision ID: 013
Revises: 012
Create Date: 2025-08-31 21:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поле source для указания источника заказа
    op.add_column('orders', sa.Column('source', sa.String(20), nullable=True, default='manual'))
    
    # Создаем индекс для поля source
    op.create_index('ix_orders_source', 'orders', ['source'])


def downgrade() -> None:
    # Удаляем индекс
    op.drop_index('ix_orders_source', 'orders')
    
    # Удаляем поле source
    op.drop_column('orders', 'source')
