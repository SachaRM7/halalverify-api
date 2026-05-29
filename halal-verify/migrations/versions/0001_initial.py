"""initial schema"""

from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


item_type = sa.Enum('food', 'cosmetic', 'restaurant', 'ingredient', name='itemtype')
halal_status = sa.Enum('halal', 'haram', 'questionable', 'unknown', name='halalstatus')
confidence_level = sa.Enum('verified', 'community', 'unknown', name='confidencelevel')
source_type = sa.Enum('certification', 'scholar', 'community', name='sourcetype')
submission_status = sa.Enum('pending', 'approved', 'rejected', name='submissionstatus')
report_status = sa.Enum('open', 'resolved', name='reportstatus')
user_role = sa.Enum('user', 'moderator', 'admin', name='userrole')


def upgrade() -> None:
    op.create_table(
        'items',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', item_type, nullable=False),
        sa.Column('status', halal_status, nullable=False),
        sa.Column('confidence', confidence_level, nullable=False),
        sa.Column('barcode', sa.String(length=64), nullable=True),
        sa.Column('community_notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_items_name', 'items', ['name'])
    op.create_index('ix_items_type', 'items', ['type'])
    op.create_index('ix_items_status', 'items', ['status'])
    op.create_index('ix_items_barcode', 'items', ['barcode'], unique=True)

    op.create_table(
        'sources',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('item_id', sa.String(length=36), sa.ForeignKey('items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_name', sa.String(length=255), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=False),
        sa.Column('source_type', source_type, nullable=False),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_sources_item_id', 'sources', ['item_id'])

    op.create_table(
        'submissions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('item_id', sa.String(length=36), sa.ForeignKey('items.id'), nullable=True),
        sa.Column('submitted_by', sa.String(length=255), nullable=False),
        sa.Column('submitted_data', sa.JSON(), nullable=False),
        sa.Column('status', submission_status, nullable=False),
        sa.Column('reviewed_by', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'reports',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('item_id', sa.String(length=36), sa.ForeignKey('items.id'), nullable=False),
        sa.Column('reporter_id', sa.String(length=255), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', report_status, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_reports_item_id', 'reports', ['item_id'])

    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('telegram_id', sa.String(length=64), nullable=True),
        sa.Column('reputation_score', sa.Integer(), nullable=False),
        sa.Column('submission_count', sa.Integer(), nullable=False),
        sa.Column('role', user_role, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_users_telegram_id', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_reports_item_id', table_name='reports')
    op.drop_table('reports')
    op.drop_table('submissions')
    op.drop_index('ix_sources_item_id', table_name='sources')
    op.drop_table('sources')
    op.drop_index('ix_items_barcode', table_name='items')
    op.drop_index('ix_items_status', table_name='items')
    op.drop_index('ix_items_type', table_name='items')
    op.drop_index('ix_items_name', table_name='items')
    op.drop_table('items')
