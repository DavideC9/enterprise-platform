from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4710b744e17b'
down_revision: Union[str, None] = '213d5ab7adb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column("sections", sa.Column("images", sa.JSON(), nullable=True))

def downgrade() -> None:
    op.drop_column("sections", "images")
