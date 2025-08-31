"""Fix photo file paths

Revision ID: 009
Revises: 008
Create Date: 2025-08-30 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    """Исправляем пути к фотографиям, заменяя обратные слеши на прямые"""
    # Получаем соединение с БД
    connection = op.get_bind()
    
    # Обновляем существующие пути к фотографиям
    connection.execute(
        sa.text("UPDATE product_photos SET file_path = REPLACE(file_path, '\\\\', '/')")
    )
    
    # Также исправляем пути, которые начинаются с 'app\\static' на 'app/static'
    connection.execute(
        sa.text("UPDATE product_photos SET file_path = REPLACE(file_path, 'app\\\\static', 'app/static')")
    )


def downgrade():
    """Возвращаем обратные слеши в путях (для Windows)"""
    connection = op.get_bind()
    
    # Заменяем прямые слеши на обратные для Windows
    connection.execute(
        sa.text("UPDATE product_photos SET file_path = REPLACE(file_path, '/', '\\\\')")
    )
    
    # Также исправляем пути, которые начинаются с 'app/static' на 'app\\static'
    connection.execute(
        sa.text("UPDATE product_photos SET file_path = REPLACE(file_path, 'app/static', 'app\\\\static')")
    )
