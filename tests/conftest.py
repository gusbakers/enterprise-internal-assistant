import json
import os
import sqlite3

import pytest

from crestline.config import ROOT


class FixtureDatabase:
    """Unit-test adapter only. Deployment always uses PostgreSQL/pgvector."""
    def __init__(self):
        self.conn=sqlite3.connect(':memory:')
        self.conn.row_factory=sqlite3.Row
        self.conn.execute("ATTACH DATABASE ':memory:' AS crestline")
        for table,rows in json.loads((ROOT/'data/business.json').read_text()).items():
            columns=','.join(f'"{key}" '+('REAL' if isinstance(value,(int,float)) else 'TEXT') for key,value in rows[0].items())
            self.conn.execute(f'CREATE TABLE crestline.{table} ({columns})')
            self.conn.executemany(f'INSERT INTO crestline.{table} VALUES ({",".join("?" for _ in rows[0])})',[list(row.values()) for row in rows])
    def read(self,sql,params=()):
        return [dict(r) for r in self.conn.execute(sql.replace('%s','?'),params)]


@pytest.fixture
def database(monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY',raising=False)
    if os.getenv('DATABASE_URL'):
        from crestline.database import Database
        return Database()
    return FixtureDatabase()
