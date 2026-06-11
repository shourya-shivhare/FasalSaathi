"""add_identity_and_profiles_phase_a

Revision ID: d03838f7228d
Revises: f20af12cc678
Create Date: 2026-06-07 12:53:43.636165

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd03838f7228d'
down_revision: Union[str, Sequence[str], None] = 'f20af12cc678'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    bind = op.get_bind()
    
    # Pre-create enum types for Postgres
    sa.Enum('ENGLISH', 'HINDI', name='preferredlanguage').create(bind)
    sa.Enum('CLAY', 'LOAMY', 'SANDY', 'BLACK', 'RED', 'SILT', name='soiltype_v2').create(bind)
    sa.Enum('RAINFED', 'BOREWELL', 'CANAL', 'DRIP', 'SPRINKLER', name='irrigationsource').create(bind)
    sa.Enum('ACTIVE', 'SUSPENDED', 'BLOCKED', 'DELETED', name='accountstatus').create(bind)
    sa.Enum('FARMER', 'ADMIN', name='userrole').create(bind)
    
    # Create new tables
    op.create_table('rate_limit_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('identifier', sa.String(length=128), nullable=False),
    sa.Column('event_type', sa.String(length=50), nullable=False),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rate_limit_events_created_at'), 'rate_limit_events', ['created_at'], unique=False)
    op.create_index(op.f('ix_rate_limit_events_event_type'), 'rate_limit_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_rate_limit_events_id'), 'rate_limit_events', ['id'], unique=False)
    op.create_index(op.f('ix_rate_limit_events_identifier'), 'rate_limit_events', ['identifier'], unique=False)
    
    op.create_table('farmer_profiles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('gender', postgresql.ENUM('MALE', 'FEMALE', 'OTHER', name='gender', create_type=False), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.Column('district', sa.String(), nullable=True),
    sa.Column('village', sa.String(), nullable=True),
    sa.Column('farm_size_acres', sa.Float(), nullable=True),
    sa.Column('annual_income', sa.Float(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('preferred_language', postgresql.ENUM('ENGLISH', 'HINDI', name='preferredlanguage', create_type=False), nullable=False, server_default='ENGLISH'),
    sa.Column('soil_type', postgresql.ENUM('CLAY', 'LOAMY', 'SANDY', 'BLACK', 'RED', 'SILT', name='soiltype_v2', create_type=False), nullable=True),
    sa.Column('irrigation_source', postgresql.ENUM('RAINFED', 'BOREWELL', 'CANAL', 'DRIP', 'SPRINKLER', name='irrigationsource', create_type=False), nullable=True),
    sa.Column('crops_grown', sa.JSON(), nullable=True),
    sa.Column('profile_completed', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('profile_version', sa.Integer(), nullable=False, server_default='1'),
    sa.Column('profile_updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_farmer_profiles_id'), 'farmer_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_farmer_profiles_user_id'), 'farmer_profiles', ['user_id'], unique=True)
    
    op.create_table('security_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('event_type', sa.String(length=50), nullable=False),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('user_agent', sa.String(length=512), nullable=True),
    sa.Column('metadata_json', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_security_events_event_type'), 'security_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_security_events_id'), 'security_events', ['id'], unique=False)
    op.create_index(op.f('ix_security_events_user_id'), 'security_events', ['user_id'], unique=False)
    
    op.create_table('sessions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('refresh_token_hash', sa.String(length=256), nullable=False),
    sa.Column('token_family_id', sa.String(length=36), nullable=False),
    sa.Column('device_info', sa.String(length=256), nullable=True),
    sa.Column('device_name', sa.String(length=128), nullable=True),
    sa.Column('is_trusted_device', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('user_agent', sa.String(length=512), nullable=True),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('last_used_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sessions_refresh_token_hash'), 'sessions', ['refresh_token_hash'], unique=True)
    op.create_index(op.f('ix_sessions_token_family_id'), 'sessions', ['token_family_id'], unique=False)
    op.create_index(op.f('ix_sessions_user_id'), 'sessions', ['user_id'], unique=False)

    # Alter farms.irrigation_source to use new irrigationsource Enum
    # 1. Cast column to String temporarily
    op.alter_column('farms', 'irrigation_source',
               existing_type=postgresql.ENUM('BOREWELL', 'CANAL', 'RAIN_FED', 'DRIP', 'SPRINKLER', 'OTHER', name='irrigationtype'),
               type_=sa.String(),
               existing_nullable=False)
    # 2. Map old values to new ones
    op.execute("UPDATE farms SET irrigation_source = 'RAINFED' WHERE irrigation_source IN ('RAIN_FED', 'OTHER')")
    # 3. Cast column to the new Enum
    op.alter_column('farms', 'irrigation_source',
               existing_type=sa.String(),
               type_=postgresql.ENUM('RAINFED', 'BOREWELL', 'CANAL', 'DRIP', 'SPRINKLER', name='irrigationsource', create_type=False),
               postgresql_using="irrigation_source::irrigationsource",
               existing_nullable=False)

    # Add new Identity Platform columns to users table
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_phone_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('phone_verified_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('account_status', sa.Column('account_status', postgresql.ENUM('ACTIVE', 'SUSPENDED', 'BLOCKED', 'DELETED', name='accountstatus', create_type=False), nullable=False, server_default='ACTIVE').type, nullable=False, server_default='ACTIVE'))
    op.add_column('users', sa.Column('role', sa.Column('role', postgresql.ENUM('FARMER', 'ADMIN', name='userrole', create_type=False), nullable=False, server_default='FARMER').type, nullable=False, server_default='FARMER'))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    
    # Make existing credentials nullable (since E.164 phone is primary now)
    op.alter_column('users', 'email', existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column('users', 'hashed_password', existing_type=sa.VARCHAR(), nullable=True)

    # Migrate data from users to farmer_profiles and normalize phone numbers
    users = bind.execute(sa.text("SELECT id, name, phone, state, district, village, age, gender, land_size_acres, category, annual_income, preferred_language, is_onboarded FROM users")).fetchall()
    for row in users:
        user_id, name, phone, state, district, village, age, gender, land_size, category, income, lang, onboarded = row
        
        # Normalize phone number to E.164 format
        phone_number = None
        if phone:
            phone_clean = phone.strip()
            if phone_clean:
                if phone_clean.startswith("+"):
                    phone_number = phone_clean
                elif len(phone_clean) == 10 and phone_clean.isdigit():
                    phone_number = f"+91{phone_clean}"
                else:
                    phone_number = phone_clean

        # Check if phone number already exists to prevent unique constraint violation
        exists = False
        if phone_number:
            existing = bind.execute(sa.text("SELECT id FROM users WHERE phone_number = :p"), {"p": phone_number}).fetchone()
            if existing:
                exists = True

        # Update user's phone_number column
        if phone_number and not exists:
            bind.execute(
                sa.text("UPDATE users SET phone_number = :p, is_phone_verified = :v, phone_verified_at = NOW() WHERE id = :id"),
                {"p": phone_number, "v": True, "id": user_id}
            )

        # Normalize gender val
        gender_val = None
        if gender:
            gender_val = str(gender).upper()
            if gender_val not in ['MALE', 'FEMALE', 'OTHER']:
                gender_val = None

        # Normalize lang val
        lang_val = 'ENGLISH'
        if lang:
            lang_val = str(lang).upper()
            if lang_val not in ['ENGLISH', 'HINDI']:
                lang_val = 'ENGLISH'

        # Insert farmer profile record
        bind.execute(
            sa.text(
                "INSERT INTO farmer_profiles (user_id, full_name, age, gender, state, district, village, farm_size_acres, annual_income, category, preferred_language, profile_completed, profile_version, created_at, updated_at) "
                "VALUES (:user_id, :full_name, :age, :gender, :state, :district, :village, :farm_size, :income, :category, :lang, :completed, 1, NOW(), NOW())"
            ),
            {
                "user_id": user_id,
                "full_name": name,
                "age": age,
                "gender": gender_val,
                "state": state,
                "district": district,
                "village": village,
                "farm_size": land_size,
                "income": income,
                "category": category,
                "lang": lang_val,
                "completed": onboarded
            }
        )

    # Finally, add index and unique constraint to phone_number
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    op.alter_column('users', 'hashed_password', existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column('users', 'email', existing_type=sa.VARCHAR(), nullable=False)
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'role')
    op.drop_column('users', 'account_status')
    op.drop_column('users', 'phone_verified_at')
    op.drop_column('users', 'is_phone_verified')
    op.drop_column('users', 'phone_number')
    
    # Restore farms.irrigation_source to legacy Enum
    op.alter_column('farms', 'irrigation_source',
               existing_type=sa.Enum('RAINFED', 'BOREWELL', 'CANAL', 'DRIP', 'SPRINKLER', name='irrigationsource'),
               type_=sa.String(),
               existing_nullable=False)
    op.execute("UPDATE farms SET irrigation_source = 'RAIN_FED' WHERE irrigation_source = 'RAINFED'")
    op.alter_column('farms', 'irrigation_source',
               existing_type=sa.String(),
               type_=postgresql.ENUM('BOREWELL', 'CANAL', 'RAIN_FED', 'DRIP', 'SPRINKLER', 'OTHER', name='irrigationtype'),
               postgresql_using="irrigation_source::irrigationtype",
               existing_nullable=False)

    op.drop_index(op.f('ix_sessions_user_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_token_family_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_refresh_token_hash'), table_name='sessions')
    op.drop_table('sessions')
    op.drop_index(op.f('ix_security_events_user_id'), table_name='security_events')
    op.drop_index(op.f('ix_security_events_id'), table_name='security_events')
    op.drop_index(op.f('ix_security_events_event_type'), table_name='security_events')
    op.drop_table('security_events')
    op.drop_index(op.f('ix_farmer_profiles_user_id'), table_name='farmer_profiles')
    op.drop_index(op.f('ix_farmer_profiles_id'), table_name='farmer_profiles')
    op.drop_table('farmer_profiles')
    op.drop_index(op.f('ix_rate_limit_events_identifier'), table_name='rate_limit_events')
    op.drop_index(op.f('ix_rate_limit_events_id'), table_name='rate_limit_events')
    op.drop_index(op.f('ix_rate_limit_events_event_type'), table_name='rate_limit_events')
    op.drop_index(op.f('ix_rate_limit_events_created_at'), table_name='rate_limit_events')
    op.drop_table('rate_limit_events')
    
    # Drop enum types
    bind = op.get_bind()
    bind.execute(sa.text("DROP TYPE preferredlanguage"))
    bind.execute(sa.text("DROP TYPE accountstatus"))
    bind.execute(sa.text("DROP TYPE userrole"))
    bind.execute(sa.text("DROP TYPE irrigationsource"))
    bind.execute(sa.text("DROP TYPE soiltype_v2"))
