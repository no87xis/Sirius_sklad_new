"""Add new fields to Order: eur_rate, client_city, payment_method, payment_note

Revision ID: 001
Revises: 
Create Date: 2025-08-28 12:45:19.303055

"""
from alembic import op
import sqlalchemy as sa
from decimal import Decimal


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем новые поля в таблицу orders
    op.add_column('orders', sa.Column('client_city', sa.String(100), nullable=True))
    op.add_column('orders', sa.Column('eur_rate', sa.Numeric(10, 4), nullable=False, server_default='0'))
    op.add_column('orders', sa.Column('payment_method', sa.String(20), nullable=False, server_default='UNPAID'))
    op.add_column('orders', sa.Column('payment_note', sa.String(120), nullable=True))


def downgrade() -> None:
    # Удаляем добавленные поля
    op.drop_column('orders', 'payment_note')
    op.drop_column('orders', 'payment_method')
    op.drop_column('orders', 'eur_rate')
    op.drop_column('orders', 'client_city')
