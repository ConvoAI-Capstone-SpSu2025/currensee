import sqlite3

import requests
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from currensee.core.settings import Settings

settings = Settings()


def create_pg_engine(db_name: str):
    engine = create_engine(
        f'{settings.POSTGRES_ENGINE_STR}/{db_name}',
        connect_args={'sslmode': 'require'}
    )

    return engine
