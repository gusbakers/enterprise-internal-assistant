"""PostgreSQL owns both business records and pgvector document embeddings."""
import hashlib
import json

import psycopg
from psycopg.rows import dict_row

from crestline.config import ROOT, MODEL_NAME, database_url
from crestline.documents import load_chunks
from crestline.embeddings import embed, vector_literal

SCHEMA = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS crestline;
CREATE TABLE IF NOT EXISTS crestline.metadata (key text PRIMARY KEY, value text NOT NULL);
CREATE TABLE IF NOT EXISTS crestline.sales (
 id integer PRIMARY KEY, product text, month integer, year integer, quarter text,
 units_sold integer, revenue numeric(16,2), market text);
CREATE TABLE IF NOT EXISTS crestline.employees (
 id integer PRIMARY KEY, department text, employee_count integer, average_salary numeric(16,2));
CREATE TABLE IF NOT EXISTS crestline.campaigns (
 id integer PRIMARY KEY, product text, campaign_name text, budget numeric(16,2), channel text,
 quarter text, year integer, impressions integer, clicks integer, conversions integer, ctr numeric);
CREATE TABLE IF NOT EXISTS crestline.metrics (
 id integer PRIMARY KEY, month integer, year integer, mrr numeric, churn_rate numeric,
 active_users integer, new_customers integer, nps_score numeric);
CREATE TABLE IF NOT EXISTS crestline.chunks (
 id text PRIMARY KEY, domain text NOT NULL, source text NOT NULL, section text NOT NULL,
 content text NOT NULL, embedding vector(384) NOT NULL);
CREATE INDEX IF NOT EXISTS chunks_domain_idx ON crestline.chunks(domain);
CREATE INDEX IF NOT EXISTS chunks_text_idx ON crestline.chunks USING gin(to_tsvector('english', content));
"""


class Database:
    def __init__(self, dsn=None):
        self.dsn = dsn or database_url()

    def connect(self):
        return psycopg.connect(self.dsn, connect_timeout=10, row_factory=dict_row)

    def read(self, sql, params=()):
        with self.connect() as conn:
            conn.execute("SET TRANSACTION READ ONLY")
            conn.execute("SET LOCAL statement_timeout = '5000ms'")
            return conn.execute(sql, params).fetchall()

    def health(self):
        return self.read("SELECT count(*) AS chunks FROM crestline.chunks")[0]

    def bootstrap(self):
        fixtures = (ROOT / "data/business.json").read_text()
        chunks = load_chunks()
        fingerprint = hashlib.sha256((fixtures + json.dumps(chunks) + MODEL_NAME).encode()).hexdigest()
        with self.connect() as conn:
            # Serialize concurrent startup attempts. Existing matching data is not re-embedded.
            conn.execute("SELECT pg_advisory_xact_lock(7481923)")
            conn.execute(SCHEMA)
            prior = conn.execute("SELECT value FROM crestline.metadata WHERE key='dataset_hash'").fetchone()
            if prior and prior["value"] == fingerprint:
                return
            if prior:
                raise RuntimeError("Dataset changed. Use a fresh demo database; automatic overwrites are disabled.")
            data = json.loads(fixtures)
            for table in ("sales", "employees", "campaigns", "metrics"):
                for row in data[table]:
                    columns = list(row)
                    sql = psycopg.sql.SQL("INSERT INTO crestline.{} ({}) VALUES ({}) ON CONFLICT (id) DO NOTHING").format(
                        psycopg.sql.Identifier(table),
                        psycopg.sql.SQL(",").join(map(psycopg.sql.Identifier, columns)),
                        psycopg.sql.SQL(",").join(psycopg.sql.Placeholder() for _ in columns))
                    conn.execute(sql, list(row.values()))
            vectors = embed([c["content"] for c in chunks])
            for chunk, vector in zip(chunks, vectors, strict=True):
                conn.execute("INSERT INTO crestline.chunks (id,domain,source,section,content,embedding) "
                             "VALUES (%s,%s,%s,%s,%s,%s::vector) ON CONFLICT (id) DO NOTHING",
                             (chunk["id"], chunk["domain"], chunk["source"], chunk["section"], chunk["content"], vector_literal(vector)))
            conn.execute("INSERT INTO crestline.metadata VALUES ('dataset_hash', %s)", (fingerprint,))


if __name__ == "__main__":
    db = Database()
    db.bootstrap()
    print("PostgreSQL + pgvector ready:", db.health())
