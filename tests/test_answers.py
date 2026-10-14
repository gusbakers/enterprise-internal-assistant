from crestline.answers import concise_evidence
from crestline.documents import load_chunks
from crestline.models import Evidence


def sources(filename):
    return [Evidence(f'S{i}',c['source']+' — '+c['section'],c['content']) for i,c in enumerate(load_chunks(),1) if filename in c['source']]


def test_remote_answer_keeps_only_requested_team():
    answer=concise_evidence('How many remote days can Engineering work?',sources('remote_work'))
    assert '4 days remote' in answer
    assert '30 consecutive' not in answer
    assert 'Standard roles' not in answer
    assert len(answer.split())<50


def test_carryover_keeps_limit_and_forfeiture():
    answer=concise_evidence('What is the maximum PTO carryover?',sources('pto_policy'))
    assert '10 days' in answer and 'forfeited on January 1st' in answer
    assert 'Sick Days' not in answer
    assert len(answer.split())<60


def test_audience_preserves_segment_context():
    answer=concise_evidence('Who is the target audience for the Crestline Watch campaign?',sources('crestline_watch_campaign'))
    assert 'Primary:' in answer and '30 to 50' in answer
    assert 'discount' not in answer


def test_api_limits_preserve_plan_and_units():
    answer=concise_evidence('What are the Cloud API rate limits?',sources('cloud_api_docs'))
    assert 'Free Tier: 100 requests per hour' in answer
    assert 'Business ($149 per month): 10,000 requests per hour' in answer
    assert 'Enterprise (custom pricing): Unlimited requests' in answer
    assert 'storage' not in answer


def test_no_candidates_does_not_invent_answer():
    assert 'narrow' in concise_evidence('unsupported question',[])
