"""add_product_code_field

Revision ID: 004
Revises: 003
Create Date: 2025-08-29 23:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поле product_code в таблицу products
    op.add_column('products', sa.Column('product_code', sa.String(6), nullable=True))
    
    # Создаем индекс для product_code
    op.create_index('ix_products_product_code', 'products', ['product_code'], unique=True)
    
    # Заполняем существующие записи случайными кодами
    # Это нужно сделать в Python коде, так как SQLite не поддерживает UPDATE с JOIN


def downgrade() -> None:
    # Удаляем индекс
    op.drop_index('ix_products_product_code', 'products')
    
    # Удаляем колонку
    op.drop_column('products', 'product_code')
