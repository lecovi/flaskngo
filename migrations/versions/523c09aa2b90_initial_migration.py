"""Initial migration

Revision ID: 523c09aa2b90
Revises: 
Create Date: 2017-01-26 18:06:08.780909

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '523c09aa2b90'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('action_groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.Column('updated_on', sa.DateTime(), nullable=False),
    sa.Column('erased', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_action_groups_description'), 'action_groups', ['description'], unique=False)
    op.create_index(op.f('ix_action_groups_id'), 'action_groups', ['id'], unique=False)
    op.create_table('auth_role_groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.Column('updated_on', sa.DateTime(), nullable=False),
    sa.Column('erased', sa.Boolean(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_role_groups_description'), 'auth_role_groups', ['description'], unique=False)
    op.create_index(op.f('ix_auth_role_groups_id'), 'auth_role_groups', ['id'], unique=False)
    op.create_index(op.f('ix_auth_role_groups_name'), 'auth_role_groups', ['name'], unique=True)
    op.create_table('auth_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.Column('updated_on', sa.DateTime(), nullable=False),
    sa.Column('erased', sa.Boolean(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('confirmed_at', sa.DateTime(), nullable=True),
    sa.Column('last_login_at', sa.DateTime(), nullable=True),
    sa.Column('last_login_ip', postgresql.INET(), nullable=True),
    sa.Column('login_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_users_email'), 'auth_users', ['email'], unique=True)
    op.create_index(op.f('ix_auth_users_id'), 'auth_users', ['id'], unique=False)
    op.create_index(op.f('ix_auth_users_username'), 'auth_users', ['username'], unique=True)
    op.create_table('actions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.Column('updated_on', sa.DateTime(), nullable=False),
    sa.Column('erased', sa.Boolean(), nullable=False),
    sa.Column('action_group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['action_group_id'], ['action_groups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_actions_description'), 'actions', ['description'], unique=False)
    op.create_index(op.f('ix_actions_id'), 'actions', ['id'], unique=False)
    op.create_table('auth_roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.Column('updated_on', sa.DateTime(), nullable=False),
    sa.Column('erased', sa.Boolean(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('role_group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_group_id'], ['auth_role_groups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_roles_description'), 'auth_roles', ['description'], unique=False)
    op.create_index(op.f('ix_auth_roles_id'), 'auth_roles', ['id'], unique=False)
    op.create_index(op.f('ix_auth_roles_name'), 'auth_roles', ['name'], unique=True)
    op.create_table('auth_users_roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.Column('updated_on', sa.DateTime(), nullable=False),
    sa.Column('erased', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['auth_roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['auth_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_users_roles_id'), 'auth_users_roles', ['id'], unique=False)
    op.create_table('event_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('action_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('params', postgresql.JSON(), nullable=True),
    sa.Column('response', postgresql.JSON(), nullable=True),
    sa.Column('code_version', sa.String(length=15), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['action_id'], ['actions.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['auth_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_logs_code_version'), 'event_logs', ['code_version'], unique=False)
    op.create_index(op.f('ix_event_logs_id'), 'event_logs', ['id'], unique=False)
    op.create_index(op.f('ix_event_logs_url'), 'event_logs', ['url'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_event_logs_url'), table_name='event_logs')
    op.drop_index(op.f('ix_event_logs_id'), table_name='event_logs')
    op.drop_index(op.f('ix_event_logs_code_version'), table_name='event_logs')
    op.drop_table('event_logs')
    op.drop_index(op.f('ix_auth_users_roles_id'), table_name='auth_users_roles')
    op.drop_table('auth_users_roles')
    op.drop_index(op.f('ix_auth_roles_name'), table_name='auth_roles')
    op.drop_index(op.f('ix_auth_roles_id'), table_name='auth_roles')
    op.drop_index(op.f('ix_auth_roles_description'), table_name='auth_roles')
    op.drop_table('auth_roles')
    op.drop_index(op.f('ix_actions_id'), table_name='actions')
    op.drop_index(op.f('ix_actions_description'), table_name='actions')
    op.drop_table('actions')
    op.drop_index(op.f('ix_auth_users_username'), table_name='auth_users')
    op.drop_index(op.f('ix_auth_users_id'), table_name='auth_users')
    op.drop_index(op.f('ix_auth_users_email'), table_name='auth_users')
    op.drop_table('auth_users')
    op.drop_index(op.f('ix_auth_role_groups_name'), table_name='auth_role_groups')
    op.drop_index(op.f('ix_auth_role_groups_id'), table_name='auth_role_groups')
    op.drop_index(op.f('ix_auth_role_groups_description'), table_name='auth_role_groups')
    op.drop_table('auth_role_groups')
    op.drop_index(op.f('ix_action_groups_id'), table_name='action_groups')
    op.drop_index(op.f('ix_action_groups_description'), table_name='action_groups')
    op.drop_table('action_groups')
    # ### end Alembic commands ###
