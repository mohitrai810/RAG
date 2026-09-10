"""add hnsw vector index

Revision ID: 640befe7bb06
Revises: 38b0fd0d6098
Create Date: 2026-09-10 22:48:44.982891
"""

from typing import Sequence, Union

from alembic import op


revision: str = "640befe7bb06"
down_revision: Union[str, Sequence[str], None] = "38b0fd0d6098"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX ix_chunks_embedding_hnsw
        ON chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS ix_chunks_embedding_hnsw
        """
    )