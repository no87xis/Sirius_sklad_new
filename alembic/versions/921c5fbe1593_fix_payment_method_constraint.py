"""fix_payment_method_constraint

Revision ID: 921c5fbe1593
Revises: 013
Create Date: 2025-09-01 02:03:14.002246

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '921c5fbe1593'
down_revision = '013'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Исправляем проблему с payment_method constraint"""
    # Получаем соединение с базой данных
    connection = op.get_bind()
    
    # 1. Обновляем все записи с 'UNPAID' на 'unpaid'
    connection.execute(sa.text("UPDATE orders SET payment_method = 'unpaid' WHERE payment_method = 'UNPAID'"))
    
    # 2. Удаляем старую колонку payment_method
    op.drop_column('orders', 'payment_method')
    
    # 3. Создаем новую колонку payment_method как ENUM
    payment_method_enum = sa.Enum('card', 'cash', 'unpaid', 'other', name='paymentmethod')
    op.add_column('orders', sa.Column('payment_method', payment_method_enum, nullable=False, server_default='unpaid'))


def downgrade() -> None:
    """Откат изменений"""
    # Получаем соединение с базой данных
    connection = op.get_bind()
    
    # 1. Обновляем все записи с 'unpaid' на 'UNPAID'
    connection.execute(sa.text("UPDATE orders SET payment_method = 'UNPAID' WHERE payment_method = 'unpaid'"))
    
    # 2. Удаляем новую колонку payment_method
    op.drop_column('orders', 'payment_method')
    
    # 3. Создаем старую колонку payment_method как String
    op.add_column('orders', sa.Column('payment_method', sa.String(20), nullable=False, server_default='UNPAID'))
