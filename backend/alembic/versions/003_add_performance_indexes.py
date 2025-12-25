"""add performance indexes for common queries

Revision ID: 003
Revises: 002
Create Date: 2025-12-25 01:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add database indexes for performance optimization.

    These indexes significantly improve query performance for:
    - Timeline queries (user conversations sorted by date)
    - Agent interaction analytics
    - Conversation search
    - Feedback aggregation
    """

    # Users table indexes
    op.create_index(
        'ix_users_email_active',
        'users',
        ['email', 'is_active'],
        unique=False
    )

    op.create_index(
        'ix_users_created_at',
        'users',
        ['created_at'],
        unique=False
    )

    # Conversations table indexes (most critical for performance)
    # Already has ix_conversations_user_created and ix_conversations_user_updated from initial schema

    # Additional conversation indexes
    op.create_index(
        'ix_conversations_ended_at',
        'conversations',
        ['ended_at'],
        unique=False
    )

    op.create_index(
        'ix_conversations_message_count',
        'conversations',
        ['message_count'],
        unique=False
    )

    # Agent interactions table indexes
    op.create_index(
        'ix_agent_interactions_agent_id',
        'agent_interactions',
        ['agent_id'],
        unique=False
    )

    op.create_index(
        'ix_agent_interactions_agent_type',
        'agent_interactions',
        ['agent_type'],
        unique=False
    )

    op.create_index(
        'ix_agent_interactions_created_at',
        'agent_interactions',
        ['created_at'],
        unique=False
    )

    op.create_index(
        'ix_agent_interactions_conv_agent',
        'agent_interactions',
        ['conversation_id', 'agent_id'],
        unique=False
    )

    # Feedbacks table indexes
    op.create_index(
        'ix_feedbacks_user_id',
        'feedbacks',
        ['user_id'],
        unique=False
    )

    op.create_index(
        'ix_feedbacks_rating',
        'feedbacks',
        ['rating'],
        unique=False
    )

    op.create_index(
        'ix_feedbacks_helpful',
        'feedbacks',
        ['helpful'],
        unique=False
    )

    op.create_index(
        'ix_feedbacks_created_at',
        'feedbacks',
        ['created_at'],
        unique=False
    )

    # Composite indexes for complex queries
    op.create_index(
        'ix_feedbacks_user_created',
        'feedbacks',
        ['user_id', 'created_at'],
        unique=False
    )


def downgrade():
    """Remove performance indexes."""

    # Drop feedbacks indexes
    op.drop_index('ix_feedbacks_user_created', table_name='feedbacks')
    op.drop_index('ix_feedbacks_created_at', table_name='feedbacks')
    op.drop_index('ix_feedbacks_helpful', table_name='feedbacks')
    op.drop_index('ix_feedbacks_rating', table_name='feedbacks')
    op.drop_index('ix_feedbacks_user_id', table_name='feedbacks')

    # Drop agent interactions indexes
    op.drop_index('ix_agent_interactions_conv_agent', table_name='agent_interactions')
    op.drop_index('ix_agent_interactions_created_at', table_name='agent_interactions')
    op.drop_index('ix_agent_interactions_agent_type', table_name='agent_interactions')
    op.drop_index('ix_agent_interactions_agent_id', table_name='agent_interactions')

    # Drop conversations indexes
    op.drop_index('ix_conversations_message_count', table_name='conversations')
    op.drop_index('ix_conversations_ended_at', table_name='conversations')

    # Drop users indexes
    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_index('ix_users_email_active', table_name='users')
