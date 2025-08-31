"""Add QR fields to orders

Revision ID: 012
Revises: 010
Create Date: 2025-08-31 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '012'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade():
    """Add QR fields to shop_orders table"""
    
    # Add QR fields to shop_orders table
    op.add_column('shop_orders', sa.Column('qr_payload', sa.Text(), nullable=True))
    op.add_column('shop_orders', sa.Column('qr_image_path', sa.Text(), nullable=True))
    op.add_column('shop_orders', sa.Column('qr_generated_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create unique index on qr_payload for fast lookups
    op.create_index('ix_shop_orders_qr_payload', 'shop_orders', ['qr_payload'], unique=True)
    
    # Create index on qr_generated_at for background processing
    op.create_index('ix_shop_orders_qr_generated_at', 'shop_orders', ['qr_generated_at'])


def downgrade():
    """Remove QR fields from shop_orders table"""
    
    # Drop indexes
    op.drop_index('ix_shop_orders_qr_generated_at', table_name='shop_orders')
    op.drop_index('ix_shop_orders_qr_payload', table_name='shop_orders')
    
    # Drop columns
    op.drop_column('shop_orders', 'qr_generated_at')
    op.drop_column('shop_orders', 'qr_image_path')
    op.drop_column('shop_orders', 'qr_payload')
