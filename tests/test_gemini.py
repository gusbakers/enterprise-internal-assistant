import json
from unittest.mock import MagicMock,patch

from crestline.gemini import Gemini
from crestline.models import Evidence


def response(answer,ids=None):
    r=MagicMock()
    r.json.return_value={'candidates':[{'content':{'parts':[{'text':json.dumps({'answer':answer,'sources':ids or ['S1'],'supported':True})}]}}]}
    return r


def test_missing_key_is_explicit(monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY',raising=False)
    assert Gemini().answer('q',[Evidence('S1','source','30 employees')],'English')[0] is None


def test_valid_citation(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','unit-test-placeholder')
    with patch('crestline.gemini.httpx.Client') as client:
        client.return_value.__enter__.return_value.post.return_value=response('There are 30 employees [S1].')
        text,notice=Gemini().answer('q',[Evidence('S1','source','30 employees')],'English')
        assert text and not notice


def test_invented_number_rejected(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','unit-test-placeholder')
    with patch('crestline.gemini.httpx.Client') as client:
        client.return_value.__enter__.return_value.post.return_value=response('There are 90 employees [S1].')
        assert Gemini().answer('q',[Evidence('S1','source','30 employees')],'English')[0] is None


def test_invented_source_rejected(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','unit-test-placeholder')
    with patch('crestline.gemini.httpx.Client') as client:
        client.return_value.__enter__.return_value.post.return_value=response('There are 30 employees [S9].',['S9'])
        assert Gemini().answer('q',[Evidence('S1','source','30 employees')],'English')[0] is None
