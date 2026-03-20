"""create logs table with optimized indexes

Revision ID: 001
Revises:
Create Date: 2026-03-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TIMESTAMP

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create logs table with timestamptz column
    op.create_table(
        'logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('timestamp', TIMESTAMP(timezone=True), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('source', sa.String(100), nullable=False),
    )

    # BRIN index on timestamp for time-series queries (small, fast for sequential data)
    op.execute("""
        CREATE INDEX idx_logs_timestamp_brin ON logs USING BRIN (timestamp)
        WITH (pages_per_range = 128, autosummarize = on)
    """)

    # B-tree indexes on frequently filtered columns
    op.create_index('idx_logs_severity', 'logs', ['severity'])
    op.create_index('idx_logs_source', 'logs', ['source'])

    # Composite B-tree index for multi-column filtering (timestamp DESC for recent logs first)
    # Column order matters: timestamp (highest cardinality, range queries), severity, source
    op.create_index(
        'idx_logs_composite',
        'logs',
        [sa.text('timestamp DESC'), 'severity', 'source'],
        postgresql_using='btree'
    )


def downgrade():
    # Drop indexes first (in reverse order)
    op.drop_index('idx_logs_composite')
    op.drop_index('idx_logs_source')
    op.drop_index('idx_logs_severity')
    op.execute('DROP INDEX IF EXISTS idx_logs_timestamp_brin')

    # Drop table
    op.drop_table('logs')
