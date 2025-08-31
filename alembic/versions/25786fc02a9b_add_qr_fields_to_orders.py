"""add_qr_fields_to_orders

Revision ID: 25786fc02a9b
Revises: 83480427e3b3
Create Date: 2025-09-01 02:16:34.185253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25786fc02a9b'
down_revision = '83480427e3b3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Добавляем поля для QR-кодов в таблицу orders"""
    # Добавляем поля для QR-кода
    op.add_column('orders', sa.Column('qr_payload', sa.String(), nullable=True))
    op.add_column('orders', sa.Column('qr_image_path', sa.String(), nullable=True))
    op.add_column('orders', sa.Column('qr_generated_at', sa.DateTime(timezone=True), nullable=True))
    
    # Создаем индекс для qr_payload
    op.create_index('ix_orders_qr_payload', 'orders', ['qr_payload'])


def downgrade() -> None:
    """Откат изменений"""
    # Удаляем индекс
    op.drop_index('ix_orders_qr_payload', 'orders')
    
    # Удаляем колонки
    op.drop_column('orders', 'qr_generated_at')
    op.drop_column('orders', 'qr_image_path')
    op.drop_column('orders', 'qr_payload')
