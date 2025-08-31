"""Remove product_code field from products

Revision ID: 008
Revises: 007
Create Date: 2025-08-30 14:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    # Удаляем поле product_code и его индекс
    op.drop_index('ix_products_product_code', table_name='products')
    op.drop_column('products', 'product_code')


def downgrade():
    # Восстанавливаем поле product_code
    op.add_column('products', sa.Column('product_code', sa.String(6), nullable=True))
    op.create_index('ix_products_product_code', 'products', ['product_code'])
