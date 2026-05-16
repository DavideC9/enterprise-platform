from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '213d5ab7adb5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sections", sa.Column("slug", sa.String(length=255), nullable=True))
    op.add_column("sections", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("sections", sa.Column("address", sa.String(length=500), nullable=True))
    op.add_column("sections", sa.Column("status", sa.String(length=100), nullable=True))
    op.add_column("sections", sa.Column("features", sa.JSON(), nullable=True))

    op.execute("UPDATE sections SET slug = key WHERE slug IS NULL")


def downgrade() -> None:
    op.drop_column("sections", "features")
    op.drop_column("sections", "status")
    op.drop_column("sections", "address")
    op.drop_column("sections", "description")
    op.drop_column("sections", "slug")