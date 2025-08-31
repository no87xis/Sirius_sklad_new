"""add_shop_tables

Revision ID: 006
Revises: 005
Create Date: 2025-08-29 23:58:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем таблицу для фото товаров
    op.create_table('product_photos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('is_main', sa.Boolean(), nullable=False, default=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_product_photos_product_id', 'product_photos', ['product_id'])
    
    # Создаем таблицу для корзины магазина
    op.create_table('shop_carts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, default=1),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_shop_carts_session_id', 'shop_carts', ['session_id'])
    op.create_index('ix_shop_carts_product_id', 'shop_carts', ['product_id'])
    
    # Создаем таблицу для заказов магазина
    op.create_table('shop_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_code', sa.String(length=8), nullable=False),
        sa.Column('order_code_last4', sa.String(length=4), nullable=False),
        sa.Column('customer_name', sa.String(length=200), nullable=False),
        sa.Column('customer_phone', sa.String(length=20), nullable=False),
        sa.Column('customer_city', sa.String(length=100), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('product_name', sa.String(length=200), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price_rub', sa.NUMERIC(precision=10, scale=2), nullable=False),
        sa.Column('total_amount', sa.NUMERIC(precision=10, scale=2), nullable=False),
        sa.Column('payment_method_id', sa.Integer(), nullable=True),
        sa.Column('payment_method_name', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='reserved'),
        sa.Column('reserved_until', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expected_delivery_date', sa.DATE(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['payment_method_id'], ['payment_methods.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_shop_orders_order_code', 'shop_orders', ['order_code'], unique=True)
    op.create_index('ix_shop_orders_order_code_last4', 'shop_orders', ['order_code_last4'])
    op.create_index('ix_shop_orders_customer_phone', 'shop_orders', ['customer_phone'])
    op.create_index('ix_shop_orders_status', 'shop_orders', ['status'])
    op.create_index('ix_shop_orders_reserved_until', 'shop_orders', ['reserved_until'])


def downgrade() -> None:
    # Удаляем таблицы в обратном порядке
    op.drop_table('shop_orders')
    op.drop_table('shop_carts')
    op.drop_table('product_photos')
