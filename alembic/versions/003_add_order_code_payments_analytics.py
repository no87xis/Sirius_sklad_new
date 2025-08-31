"""Add order code, payments analytics and product availability

Revision ID: 003
Revises: 002
Create Date: 2025-08-28 21:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
import random
import string
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def generate_order_code() -> str:
    """Генерирует уникальный 8-символьный код заказа"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def upgrade() -> None:
    """Добавляем новые возможности в систему"""
    connection = op.get_bind()
    
    # 1. Добавляем новые поля в таблицу orders
    op.add_column('orders', sa.Column('order_code', sa.String(8), nullable=True))
    op.add_column('orders', sa.Column('order_code_last4', sa.String(4), nullable=True))
    op.add_column('orders', sa.Column('payment_method_id', sa.Integer(), nullable=True))
    op.add_column('orders', sa.Column('payment_instrument_id', sa.Integer(), nullable=True))
    op.add_column('orders', sa.Column('paid_amount', sa.Numeric(10, 2), nullable=True))
    op.add_column('orders', sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True))
    
    # 2. Добавляем новые поля в таблицу products
    op.add_column('products', sa.Column('availability_status', sa.String(20), nullable=True, default='IN_STOCK'))
    op.add_column('products', sa.Column('expected_date', sa.Date(), nullable=True))
    
    # 3. Создаем таблицу payment_methods
    op.create_table('payment_methods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 4. Создаем таблицу payment_instruments
    op.create_table('payment_instruments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('method_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['method_id'], ['payment_methods.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 5. Создаем таблицу cash_flows
    op.create_table('cash_flows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('direction', sa.String(20), nullable=False),  # INFLOW/OUTFLOW
        sa.Column('source_method_id', sa.Integer(), nullable=False),
        sa.Column('source_instrument_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('reason', sa.String(200), nullable=True),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['source_method_id'], ['payment_methods.id'], ),
        sa.ForeignKeyConstraint(['source_instrument_id'], ['payment_instruments.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 6. Создаем индексы для производительности
    op.create_index('ix_orders_order_code', 'orders', ['order_code'], unique=True)
    op.create_index('ix_orders_order_code_last4', 'orders', ['order_code_last4'])
    op.create_index('ix_orders_payment_method_id', 'orders', ['payment_method_id'])
    op.create_index('ix_orders_payment_instrument_id', 'orders', ['payment_instrument_id'])
    op.create_index('ix_products_availability_status', 'products', ['availability_status'])
    op.create_index('ix_cash_flows_datetime', 'cash_flows', ['datetime'])
    op.create_index('ix_cash_flows_direction', 'cash_flows', ['direction'])
    op.create_index('ix_cash_flows_source_method_id', 'cash_flows', ['source_method_id'])
    op.create_index('ix_payment_methods_name', 'payment_methods', ['name'], unique=True)
    op.create_index('ix_payment_instruments_name_method', 'payment_instruments', ['name', 'method_id'], unique=True)
    
    # 7. Заполняем базовые методы оплаты
    payment_methods = [
        {'name': 'Наличные на складе', 'type': 'cash'},
        {'name': 'Перевод на карту', 'type': 'card'},
        {'name': 'USDT', 'type': 'crypto'},
        {'name': 'Банковский перевод', 'type': 'bank'},
        {'name': 'Другой способ', 'type': 'other'}
    ]
    
    for method in payment_methods:
        connection.execute(text("""
            INSERT INTO payment_methods (name, type, is_active, created_at)
            VALUES (:name, :type, :is_active, :created_at)
        """), {
            'name': method['name'],
            'type': method['type'],
            'is_active': True,
            'created_at': datetime.utcnow()
        })
    
    # 8. Генерируем order_code для существующих заказов
    orders = connection.execute(text("SELECT id FROM orders WHERE order_code IS NULL")).fetchall()
    
    for order in orders:
        order_id = order[0]  # Получаем ID из кортежа
        order_code = generate_order_code()
        # Проверяем уникальность
        while connection.execute(text("SELECT COUNT(*) FROM orders WHERE order_code = :code"), {'code': order_code}).scalar() > 0:
            order_code = generate_order_code()
        
        connection.execute(text("""
            UPDATE orders 
            SET order_code = :code, order_code_last4 = :last4
            WHERE id = :id
        """), {
            'code': order_code,
            'last4': order_code[-4:],
            'id': order_id
        })
    
    # 9. Устанавливаем дефолтные значения для существующих товаров
    connection.execute(text("""
        UPDATE products 
        SET availability_status = 'IN_STOCK' 
        WHERE availability_status IS NULL
    """))
    
    # 10. Устанавливаем дефолтные значения для существующих заказов
    connection.execute(text("""
        UPDATE orders 
        SET payment_method_id = (
            SELECT id FROM payment_methods WHERE name = 'Другой способ' LIMIT 1
        )
        WHERE payment_method_id IS NULL
    """))


def downgrade() -> None:
    """Откат изменений"""
    # Удаляем индексы
    op.drop_index('ix_cash_flows_source_method_id', 'cash_flows')
    op.drop_index('ix_cash_flows_direction', 'cash_flows')
    op.drop_index('ix_cash_flows_datetime', 'cash_flows')
    op.drop_index('ix_products_availability_status', 'products')
    op.drop_index('ix_orders_payment_instrument_id', 'orders')
    op.drop_index('ix_orders_payment_method_id', 'orders')
    op.drop_index('ix_orders_order_code_last4', 'orders')
    op.drop_index('ix_orders_order_code', 'orders')
    op.drop_index('ix_payment_instruments_name_method', 'payment_instruments')
    op.drop_index('ix_payment_methods_name', 'payment_methods')
    
    # Удаляем таблицы
    op.drop_table('cash_flows')
    op.drop_table('payment_instruments')
    op.drop_table('payment_methods')
    
    # Удаляем колонки из products
    op.drop_column('products', 'expected_date')
    op.drop_column('products', 'availability_status')
    
    # Удаляем колонки из orders
    op.drop_column('orders', 'paid_at')
    op.drop_column('orders', 'paid_amount')
    op.drop_column('orders', 'payment_instrument_id')
    op.drop_column('orders', 'payment_method_id')
    op.drop_column('orders', 'order_code_last4')
    op.drop_column('orders', 'order_code')
