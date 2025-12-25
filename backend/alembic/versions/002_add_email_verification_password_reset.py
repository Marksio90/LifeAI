"""add email verification and password reset fields

Revision ID: 002
Revises: 001
Create Date: 2025-12-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Add email verification and password reset fields to users table."""
    # Add email verification columns
    op.add_column('users', sa.Column('verification_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('verification_token_expires', sa.DateTime(), nullable=True))

    # Add password reset columns
    op.add_column('users', sa.Column('password_reset_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('password_reset_token_expires', sa.DateTime(), nullable=True))


def downgrade():
    """Remove email verification and password reset fields from users table."""
    # Remove password reset columns
    op.drop_column('users', 'password_reset_token_expires')
    op.drop_column('users', 'password_reset_token')

    # Remove email verification columns
    op.drop_column('users', 'verification_token_expires')
    op.drop_column('users', 'verification_token')
