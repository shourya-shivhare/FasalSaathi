"""remove_legacy_user_profile_columns

Revision ID: f4666ebe4550
Revises: d03838f7228d
Create Date: 2026-06-07 13:18:49.802694

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4666ebe4550'
down_revision: Union[str, Sequence[str], None] = 'd03838f7228d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Copy phone to phone_number before dropping phone, ensuring no duplicates violate unique constraint
    op.execute("""
        UPDATE users 
        SET phone_number = phone 
        WHERE phone_number IS NULL 
          AND phone IS NOT NULL 
          AND id = (SELECT MIN(u.id) FROM users u WHERE u.phone = users.phone)
    """)
    op.drop_column('users', 'phone')
    op.drop_column('users', 'state')
    op.drop_column('users', 'district')
    op.drop_column('users', 'village')
    op.drop_column('users', 'age')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'land_size_acres')
    op.drop_column('users', 'category')
    op.drop_column('users', 'annual_income')
    op.drop_column('users', 'preferred_language')
    op.drop_column('users', 'is_onboarded')


def downgrade() -> None:
    """Downgrade schema."""
    from sqlalchemy.dialects import postgresql
    
    op.add_column('users', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('users', sa.Column('state', sa.String(), nullable=True))
    op.add_column('users', sa.Column('district', sa.String(), nullable=True))
    op.add_column('users', sa.Column('village', sa.String(), nullable=True))
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('gender', postgresql.ENUM('MALE', 'FEMALE', 'OTHER', name='gender', create_type=False), nullable=True))
    op.add_column('users', sa.Column('land_size_acres', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('category', sa.String(), nullable=True))
    op.add_column('users', sa.Column('annual_income', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('preferred_language', postgresql.ENUM('ENGLISH', 'HINDI', name='language', create_type=False), nullable=False, server_default='ENGLISH'))
    op.add_column('users', sa.Column('is_onboarded', sa.Boolean(), nullable=False, server_default='false'))
