from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db93df92fcac'
down_revision: Union[str, None] = '4710b744e17b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'sections',
        sa.Column(
            'sort_order',
            sa.Integer(),
            nullable=False,
            server_default='0'
        )
    )

    op.create_index(
        op.f('ix_sections_sort_order'),
        'sections',
        ['sort_order'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_sections_sort_order'), table_name='sections')
    op.drop_column('sections', 'sort_order')