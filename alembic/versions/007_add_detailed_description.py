"""Add detailed_description field to products

Revision ID: 007
Revises: 006
Create Date: 2025-08-30 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем поле detailed_description
    op.add_column('products', sa.Column('detailed_description', sa.Text(), nullable=True))


def downgrade():
    # Удаляем поле detailed_description
    op.drop_column('products', 'detailed_description')
