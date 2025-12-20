"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2025-12-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('preferred_language', sa.String(length=10), nullable=True, server_default='pl'),
        sa.Column('preferred_voice', sa.String(length=50), nullable=True, server_default='nova'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_premium', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('preferences', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('mfa_enabled', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('mfa_secret', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create conversations table
    op.create_table('conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True, server_default='pl'),
        sa.Column('messages', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('agents_used', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('main_topics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)
    op.create_index(op.f('ix_conversations_session_id'), 'conversations', ['session_id'], unique=True)

    # Create feedbacks table
    op.create_table('feedbacks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('message_index', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.String(length=100), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('helpful', sa.Boolean(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('relevance', sa.Float(), nullable=True),
        sa.Column('clarity', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feedbacks_user_id'), 'feedbacks', ['user_id'], unique=False)
    op.create_index(op.f('ix_feedbacks_conversation_id'), 'feedbacks', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_feedbacks_agent_id'), 'feedbacks', ['agent_id'], unique=False)

    # Create agent_interactions table
    op.create_table('agent_interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', sa.String(length=100), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('user_message', sa.Text(), nullable=False),
        sa.Column('agent_response', sa.Text(), nullable=False),
        sa.Column('intent_type', sa.String(length=100), nullable=True),
        sa.Column('intent_confidence', sa.Float(), nullable=True),
        sa.Column('routing_type', sa.String(length=50), nullable=True),
        sa.Column('response_time_ms', sa.Float(), nullable=True),
        sa.Column('tokens_used', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('context_enriched', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_interactions_conversation_id'), 'agent_interactions', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_agent_interactions_agent_id'), 'agent_interactions', ['agent_id'], unique=False)
    op.create_index(op.f('ix_agent_interactions_agent_type'), 'agent_interactions', ['agent_type'], unique=False)


def downgrade():
    op.drop_table('agent_interactions')
    op.drop_table('feedbacks')
    op.drop_table('conversations')
    op.drop_table('users')
