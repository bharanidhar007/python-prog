Always show details
# Continue building the project structure, finish files, create Alembic migrations, and zip it.
import os, textwrap, zipfile, shutil, datetime, pathlib

base = "/mnt/data/fiducia_crm_fastapi"
assert os.path.exists(base), "Project root missing; please re-run previous cell if this fails."

def w(path, content):
    full = os.path.join(base, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content).lstrip())

# __init__ placeholders
for d in [
    "app",
    "app/api",
    "app/api/v1",
    "app/api/v1/routers",
    "app/core",
    "app/db",
    "app/models",
    "app/schemas",
    "app/services",
    "app/tasks",
    "scripts",
    "tests",
    "migrations",
    "migrations/versions",
]:
    w(f"{d}/__init__.py", "")

# Chats router
w("app/api/v1/routers/chats.py", """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_session
from app.models.models import Chat, Message
from app.schemas.schemas import ChatOut, MessageOut, MessageCreate

router = APIRouter(tags=["Chats"])

@router.get("/chats/{chat_id}", response_model=ChatOut)
async def get_chat(chat_id: int, session: AsyncSession = Depends(get_session)):
    chat = await session.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatOut.model_validate(chat)

@router.get("/chats/{chat_id}/messages", response_model=list[MessageOut])
async def list_messages(chat_id: int, session: AsyncSession = Depends(get_session)):
    chat = await session.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    res = await session.execute(select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at.asc()))
    return [MessageOut.model_validate(m) for m in res.scalars().all()]
""")

# Stats router
w("app/api/v1/routers/stats.py", """
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_session
from app.models.models import CRMEntry, Chat, Message

router = APIRouter(tags=["Stats"])

@router.get("/stats/summary", response_model=dict)
async def stats_summary(session: AsyncSession = Depends(get_session)):
    total_entries = (await session.execute(select(func.count()).select_from(CRMEntry))).scalar_one()
    total_chats = (await session.execute(select(func.count()).select_from(Chat))).scalar_one()
    total_messages = (await session.execute(select(func.count()).select_from(Message))).scalar_one()
    return {"total_entries": total_entries, "total_chats": total_chats, "total_messages": total_messages}
""")

# Tasks: worker and jobs
w("app/tasks/jobs.py", """
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings
from app.models.models import User, CRMEntry
from sqlalchemy import select

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def sync_crm_from_users():
    \"\"\"Populate CRM entries for users missing an entry.\"\"\"
    async with SessionLocal() as session:  # type: AsyncSession
        res = await session.execute(select(User))
        users = res.scalars().all()
        new_count = 0
        for u in users:
            exists = (await session.execute(select(CRMEntry).where(CRMEntry.user_id == u.id))).scalar_one_or_none()
            if not exists:
                entry = CRMEntry(user_id=u.id, email=u.email, display_name=u.display_name, member_type=u.member_type)
                session.add(entry)
                new_count += 1
        await session.commit()
        return {"created": new_count}
""")

w("app/tasks/worker.py", """
from arq import run_worker
from arq.connections import RedisSettings
from app.core.config import settings
from app.tasks.jobs import sync_crm_from_users

class WorkerSettings:
    functions = [sync_crm_from_users]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)

if __name__ == '__main__':
    run_worker(WorkerSettings)
""")

# Migrations env.py
w("migrations/env.py", """
from __future__ import annotations
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from alembic import context
from sqlalchemy import create_engine
from app.core.config import settings
from app.db.base import Base
from app.models import models  # ensure models are imported

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = create_engine(settings.DATABASE_URL, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
""")

# Initial migration: create core tables
w("migrations/versions/2025_01_01_000001_create_base.py", """
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '2025_01_01_000001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('user',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('external_id', sa.String(length=64), nullable=True, unique=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('member_type', sa.String(length=32), nullable=False, server_default='guest'),
    )
    op.create_index('ix_user_email', 'user', ['email'])
    op.create_index('ix_user_display_name', 'user', ['display_name'])
    op.create_index('ix_user_member_type', 'user', ['member_type'])

    op.create_table('tag',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=64), nullable=False, unique=True),
    )
    op.create_index('ix_tag_name', 'tag', ['name'])

    op.create_table('crmentry',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column
