import os

import pytest

from crestline.assistant import Assistant
from crestline.retrieval import retrieve

pytestmark=pytest.mark.skipif(not os.getenv('DATABASE_URL'),reason='Requires PostgreSQL + pgvector; exercised in CI')


@pytest.mark.parametrize('question,domain,source',[
 ('What is the maximum PTO carryover?','hr','pto_policy.txt'),
 ('How many remote days can Engineering work?','hr','remote_work_policy.txt'),
 ('What documents are needed for onboarding?','hr','onboarding_guide.txt'),
 ('Who is the target audience for the Crestline Watch campaign?','marketing','crestline_watch_campaign.txt'),
 ('What are the Cloud API rate limits?','product','cloud_api_docs.txt'),
 ('¿Cuál es la política de vacaciones?','hr','pto_policy.txt'),
])
def test_pgvector_retrieval(database,question,domain,source):
    evidence=retrieve(database,question,domain)
    assert evidence and source in evidence[0].source


def test_database_read_only(database):
    with pytest.raises(Exception):
        database.read('DELETE FROM crestline.sales')
    assert database.read('SELECT COUNT(*) AS n FROM crestline.sales')[0]['n']==60


def test_real_database_health(database):
    assert database.health()['chunks']>90
    assert database.read("SELECT extversion FROM pg_extension WHERE extname='vector'")


def test_rag_answer_has_evidence(database):
    result=Assistant(database).ask('What is the maximum PTO carryover?')
    assert result.evidence and '10 days' in result.answer
    assert result.mode=='source excerpts'
