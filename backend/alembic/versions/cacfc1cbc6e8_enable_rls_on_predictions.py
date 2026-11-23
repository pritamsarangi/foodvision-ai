"""enable_rls_on_predictions

Revision ID: cacfc1cbc6e8
Revises: edd289f98d7b
Create Date: 2026-11-23 20:52:42.930687

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cacfc1cbc6e8'
down_revision: Union[str, Sequence[str], None] = 'edd289f98d7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable RLS and FORCE it on the predictions table
    op.execute("ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE predictions FORCE ROW LEVEL SECURITY;")

    # 2. Define the multi-tenant isolation policy
    op.execute("""
        CREATE POLICY user_prediction_isolation_policy ON predictions
        FOR ALL
        USING (
            user_id = NULLIF(current_setting('app.current_user_id', true), '')
            OR (user_id IS NULL AND NULLIF(current_setting('app.current_user_id', true), '') IS NULL)
        )
        WITH CHECK (
            user_id = NULLIF(current_setting('app.current_user_id', true), '')
            OR (user_id IS NULL AND NULLIF(current_setting('app.current_user_id', true), '') IS NULL)
        );
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS user_prediction_isolation_policy ON predictions;")
    op.execute("ALTER TABLE predictions NO FORCE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE predictions DISABLE ROW LEVEL SECURITY;")
