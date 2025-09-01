"""initial schema

Revision ID: 001
Revises: 
Create Date: 2025-08-29 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create products_silver table
    op.create_table(
        'products_silver',
        sa.Column('product_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('rating', sa.Numeric(3, 1), nullable=False),
        sa.Column('in_stock', sa.Boolean(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('ingested_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('product_id')
    )
    
    # Create category_price_summary_gold table
    op.create_table(
        'category_price_summary_gold',
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('avg_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('avg_rating', sa.Numeric(3, 1), nullable=False),
        sa.Column('item_count', sa.Integer(), nullable=False),
        sa.Column('last_refresh_ts', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('category')
    )

def downgrade() -> None:
    op.drop_table('category_price_summary_gold')
    op.drop_table('products_silver')
