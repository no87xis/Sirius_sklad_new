"""add_product_enhancements

Revision ID: 010
Revises: a140102d6876
Create Date: 2025-08-30 04:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '010'
down_revision = 'a140102d6876'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Обновляем существующие товары, устанавливая статус наличия"""
    
    # Поля уже существуют, только обновляем данные
    connection = op.get_bind()
    
    # Устанавливаем статус "В наличии" для товаров с quantity > 0
    connection.execute(sa.text("""
        UPDATE products 
        SET availability_status = 'IN_STOCK' 
        WHERE quantity > 0 AND (availability_status IS NULL OR availability_status = '')
    """))
    
    # Устанавливаем статус "OUT_OF_STOCK" для товаров с quantity = 0
    connection.execute(sa.text("""
        UPDATE products 
        SET availability_status = 'OUT_OF_STOCK' 
        WHERE quantity = 0 AND (availability_status IS NULL OR availability_status = '')
    """))


def downgrade() -> None:
    """Откат не требуется, так как поля уже существовали"""
    pass
