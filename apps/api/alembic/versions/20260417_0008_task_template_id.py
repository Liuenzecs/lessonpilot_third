"""task_template_id

Revision ID: 0008_task_template_id
Revises: 0007_cycle4_template
Create Date: 2026-04-17 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0008_task_template_id'
down_revision = '0007_cycle4_template'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'tasks',
        sa.Column('template_id', sa.String(36), nullable=True),
    )
    op.create_foreign_key(
        'fk_tasks_template_id',
        'tasks',
        'templates',
        ['template_id'],
        ['id'],
    )


def downgrade() -> None:
    op.drop_constraint('fk_tasks_template_id', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'template_id')
