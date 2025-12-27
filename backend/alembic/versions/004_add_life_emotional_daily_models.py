"""Add life stage, emotional state, and daily companion models

Revision ID: 004
Revises: 003
Create Date: 2025-12-27 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_life_profiles table
    op.create_table('user_life_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('current_stage', sa.String(50), nullable=False),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('date_of_birth', sa.DateTime(), nullable=True),
        sa.Column('current_roles', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('relationship_status', sa.String(50), nullable=True),
        sa.Column('has_children', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('employment_status', sa.String(50), nullable=True),
        sa.Column('education_level', sa.String(50), nullable=True),
        sa.Column('priorities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('satisfaction', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('current_challenges', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('life_goals', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create life_transitions table
    op.create_table('life_transitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transition_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('expected_end_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('support_level_needed', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('coping_score', sa.Float(), nullable=True),
        sa.Column('notes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('emotions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['profile_id'], ['user_life_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create life_milestones table
    op.create_table('life_milestones',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('achieved_at', sa.DateTime(), nullable=False),
        sa.Column('importance', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('emotions_felt', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('reflection', sa.Text(), nullable=True),
        sa.Column('images', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['profile_id'], ['user_life_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create emotional_states table
    op.create_table('emotional_states',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('primary_emotion', sa.String(50), nullable=False),
        sa.Column('secondary_emotions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('intensity', sa.Float(), nullable=True),
        sa.Column('valence', sa.Float(), nullable=True),
        sa.Column('arousal', sa.Float(), nullable=True),
        sa.Column('mood_state', sa.String(50), nullable=True),
        sa.Column('triggers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('context', sa.Text(), nullable=True),
        sa.Column('needs_support', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_emotional_states_user_id'), 'emotional_states', ['user_id'], unique=False)

    # Create emotional_patterns table
    op.create_table('emotional_patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pattern_type', sa.String(50), nullable=False),
        sa.Column('emotions_involved', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('frequency', sa.String(50), nullable=True),
        sa.Column('intensity_trend', sa.String(50), nullable=True),
        sa.Column('common_triggers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('time_of_day', sa.String(50), nullable=True),
        sa.Column('seasonal_pattern', sa.Boolean(), nullable=True),
        sa.Column('insights', sa.Text(), nullable=True),
        sa.Column('recommendations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('first_detected', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_occurrence', sa.DateTime(), nullable=True),
        sa.Column('occurrence_count', sa.Integer(), nullable=True, server_default='1'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create empathy_responses table
    op.create_table('empathy_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('emotional_state_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('empathy_level', sa.String(50), nullable=False),
        sa.Column('response_type', sa.String(50), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=False),
        sa.Column('validation_phrases', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('support_offered', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('helpful', sa.Boolean(), nullable=True),
        sa.Column('user_feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['emotional_state_id'], ['emotional_states.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create mood_journal_entries table
    op.create_table('mood_journal_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entry_date', sa.DateTime(), nullable=False),
        sa.Column('mood_rating', sa.Integer(), nullable=False),
        sa.Column('energy_level', sa.Integer(), nullable=True),
        sa.Column('stress_level', sa.Integer(), nullable=True),
        sa.Column('sleep_quality', sa.Integer(), nullable=True),
        sa.Column('emotions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('activities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('journal_text', sa.Text(), nullable=True),
        sa.Column('gratitude_items', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('challenges', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('wins', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mood_journal_entries_user_id'), 'mood_journal_entries', ['user_id'], unique=False)
    op.create_index(op.f('ix_mood_journal_entries_entry_date'), 'mood_journal_entries', ['entry_date'], unique=False)

    # Create daily_rituals table
    op.create_table('daily_rituals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ritual_type', sa.String(50), nullable=False),
        sa.Column('time_of_day', sa.String(50), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('frequency', sa.String(50), nullable=True),
        sa.Column('reminder_enabled', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('reminder_time', sa.String(10), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create ritual_completions table
    op.create_table('ritual_completions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('ritual_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('mood_before', sa.Integer(), nullable=True),
        sa.Column('mood_after', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['ritual_id'], ['daily_rituals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create daily_check_ins table
    op.create_table('daily_check_ins',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('check_in_date', sa.DateTime(), nullable=False),
        sa.Column('check_in_type', sa.String(50), nullable=False),
        sa.Column('mood', sa.Integer(), nullable=True),
        sa.Column('energy', sa.Integer(), nullable=True),
        sa.Column('stress', sa.Integer(), nullable=True),
        sa.Column('gratitude', sa.Text(), nullable=True),
        sa.Column('intention', sa.Text(), nullable=True),
        sa.Column('reflection', sa.Text(), nullable=True),
        sa.Column('completed_rituals', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('highlights', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('challenges', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('sleep_quality', sa.Integer(), nullable=True),
        sa.Column('sleep_hours', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_daily_check_ins_user_id'), 'daily_check_ins', ['user_id'], unique=False)
    op.create_index(op.f('ix_daily_check_ins_check_in_date'), 'daily_check_ins', ['check_in_date'], unique=False)

    # Create daily_intentions table
    op.create_table('daily_intentions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('intention_date', sa.DateTime(), nullable=False),
        sa.Column('primary_intention', sa.Text(), nullable=False),
        sa.Column('focus_areas', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('specific_goals', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('affirmations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('reflection', sa.Text(), nullable=True),
        sa.Column('success_rating', sa.Integer(), nullable=True),
        sa.Column('lessons_learned', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_daily_intentions_user_id'), 'daily_intentions', ['user_id'], unique=False)

    # Create wellness_snapshots table
    op.create_table('wellness_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_date', sa.DateTime(), nullable=False),
        sa.Column('overall_wellness', sa.Float(), nullable=True),
        sa.Column('physical_health', sa.Integer(), nullable=True),
        sa.Column('mental_health', sa.Integer(), nullable=True),
        sa.Column('emotional_health', sa.Integer(), nullable=True),
        sa.Column('social_health', sa.Integer(), nullable=True),
        sa.Column('spiritual_health', sa.Integer(), nullable=True),
        sa.Column('work_satisfaction', sa.Integer(), nullable=True),
        sa.Column('life_balance', sa.Integer(), nullable=True),
        sa.Column('strengths', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('areas_for_growth', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('recommended_actions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('trends', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wellness_snapshots_user_id'), 'wellness_snapshots', ['user_id'], unique=False)


def downgrade():
    op.drop_table('wellness_snapshots')
    op.drop_table('daily_intentions')
    op.drop_table('daily_check_ins')
    op.drop_table('ritual_completions')
    op.drop_table('daily_rituals')
    op.drop_table('mood_journal_entries')
    op.drop_table('empathy_responses')
    op.drop_table('emotional_patterns')
    op.drop_table('emotional_states')
    op.drop_table('life_milestones')
    op.drop_table('life_transitions')
    op.drop_table('user_life_profiles')
