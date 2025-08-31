"""update_order_code_format

Revision ID: 005
Revises: 004
Create Date: 2025-08-29 23:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
import random
import string


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Обновляем формат кодов заказов на новый: 3 буквы + 5 цифр"""
    # Создаем временную таблицу для новых кодов
    op.execute("""
        CREATE TABLE IF NOT EXISTS temp_order_codes (
            id INTEGER PRIMARY KEY,
            new_code VARCHAR(8)
        )
    """)
    
    # Генерируем новые коды для существующих заказов
    # Это будет выполнено в Python коде после миграции


def downgrade() -> None:
    """Откатываем изменения"""
    # Удаляем временную таблицу
    op.execute("DROP TABLE IF EXISTS temp_order_codes")


def data_upgrade() -> None:
    """Обновляем данные кодов заказов"""
    # Эта функция будет вызвана отдельно для обновления данных
    pass
