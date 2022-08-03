from decouple import config
from models import db

PG_USER = config('POSTGRES_USER')
PG_PASSWORD = config('POSTGRES_PASSWORD')
PG_DB = config('POSTGRES_DB')

PG_DSN = f"postgres://{PG_USER}:{PG_PASSWORD}@db:5432/{PG_DB}"


async def init_orm(app):
    await db.set_bind(PG_DSN)
    await db.gino.create_all()
    yield
    await db.pop_bind().close()

