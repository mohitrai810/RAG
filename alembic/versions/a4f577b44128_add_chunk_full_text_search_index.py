from typing import Sequence, Union

from alembic import op


revision: str = "YOUR_GENERATED_REVISION"
down_revision: Union[str, Sequence[str], None] = "640befe7bb06"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX ix_chunks_content_fts
        ON chunks
        USING gin (to_tsvector('english', content))
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS ix_chunks_content_fts
        """
    )