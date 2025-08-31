"""fix_order_status_constraint

Revision ID: 83480427e3b3
Revises: 921c5fbe1593
Create Date: 2025-09-01 02:06:25.604560

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83480427e3b3'
down_revision = '921c5fbe1593'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Исправляем проблему с order status constraint"""
    # Получаем соединение с базой данных
    connection = op.get_bind()
    
    # 1. Обновляем все записи с неправильными статусами
    connection.execute(sa.text("UPDATE orders SET status = 'paid_not_issued' WHERE status = 'PAID_NOT_ISSUED'"))
    connection.execute(sa.text("UPDATE orders SET status = 'paid_issued' WHERE status = 'PAID_ISSUED'"))
    connection.execute(sa.text("UPDATE orders SET status = 'paid_denied' WHERE status = 'PAID_DENIED'"))
    
    # 2. Удаляем старую колонку status
    op.drop_column('orders', 'status')
    
    # 3. Создаем новую колонку status как ENUM
    order_status_enum = sa.Enum('paid_not_issued', 'paid_issued', 'paid_denied', name='orderstatus')
    op.add_column('orders', sa.Column('status', order_status_enum, nullable=False, server_default='paid_not_issued'))


def downgrade() -> None:
    """Откат изменений"""
    # Получаем соединение с базой данных
    connection = op.get_bind()
    
    # 1. Обновляем все записи обратно
    connection.execute(sa.text("UPDATE orders SET status = 'PAID_NOT_ISSUED' WHERE status = 'paid_not_issued'"))
    connection.execute(sa.text("UPDATE orders SET status = 'PAID_ISSUED' WHERE status = 'paid_issued'"))
    connection.execute(sa.text("UPDATE orders SET status = 'PAID_DENIED' WHERE status = 'paid_denied'"))
    
    # 2. Удаляем новую колонку status
    op.drop_column('orders', 'status')
    
    # 3. Создаем старую колонку status как String
    op.add_column('orders', sa.Column('status', sa.String(20), nullable=False, server_default='PAID_NOT_ISSUED'))
