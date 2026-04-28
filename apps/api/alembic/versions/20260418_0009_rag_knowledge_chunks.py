"""rag_knowledge_chunks

Revision ID: 0009_rag_knowledge_chunks
Revises: 0008_task_template_id
Create Date: 2026-04-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = '0009_rag_knowledge_chunks'
down_revision = '0008_task_template_id'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    op.create_table(
        'knowledge_chunks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('domain', sa.String(80), nullable=False, index=True),
        sa.Column('knowledge_type', sa.String(50), nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('source', sa.String(255), nullable=False),
        sa.Column('chapter', sa.String(100), nullable=True),
        sa.Column('metadata_', sa.JSON, nullable=True),
        sa.Column('embedding', Vector(1024), nullable=True),
        sa.Column('token_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.execute(
        'CREATE INDEX ix_knowledge_chunks_embedding '
        'ON knowledge_chunks USING hnsw (embedding vector_cosine_ops)'
    )


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS ix_knowledge_chunks_embedding')
    op.drop_table('knowledge_chunks')
