"""All API responses below are mocked test fixtures, NEVER recorded Meta output."""
from copy import deepcopy
import json
import pytest
import requests
from streamlit.testing.v1 import AppTest
from restaurant_lab.config import ROOT
from restaurant_lab import meta_stock as ms
from restaurant_lab.operations_demo import RECIPES
from restaurant_lab.planning import plan_prep


def candidate():
    return {'ingredients':[
        {'ingredient':'dough','quantity':10,'unit':'kg','source_quote':'Dough: ten kilograms on hand.'},
        {'ingredient':'cheese','quantity':2,'unit':'kg','source_quote':'Cheese: 2 kg counted on hand.'},
        {'ingredient':'sauce','quantity':3000,'unit':'g','source_quote':'Sauce: 3000 grams on hand.'}]}


def body():
    return {'id':'MOCK-TEST-NOT-LIVE','model':ms.MODEL,'usage':{'prompt_tokens':100,'completion_tokens':100},
            'choices':[{'finish_reason':'stop','message':{'content':json.dumps(candidate()),'refusal':None}}]}


def authorize(monkeypatch):
    monkeypatch.setenv('MODEL_API_KEY','unit-test-placeholder-not-a-real-key')
    monkeypatch.setenv('META_LIVE_ENABLED','true')


def mock_post(monkeypatch,payload=None,status=200):
    calls=[]
    class Response:
        status_code=status
        def json(self):return payload or body()
    def post(url,**kwargs):calls.append((url,kwargs));return Response()
    monkeypatch.setattr(ms.requests,'post',post)
    return calls


def test_disabled_missing_key_and_consent_send_nothing(monkeypatch):
    calls=mock_post(monkeypatch)
    monkeypatch.delenv('MODEL_API_KEY',raising=False);monkeypatch.delenv('META_LIVE_ENABLED',raising=False)
    with pytest.raises(RuntimeError):ms.extract_demo_stock(authorized=True)
    monkeypatch.setenv('META_LIVE_ENABLED','true')
    with pytest.raises(RuntimeError):ms.extract_demo_stock(authorized=True)
    authorize(monkeypatch)
    with pytest.raises(RuntimeError):ms.extract_demo_stock()
    assert calls==[]


def test_request_and_confirmation_to_plan(monkeypatch):
    authorize(monkeypatch);calls=mock_post(monkeypatch)
    record=ms.extract_demo_stock(authorized=True)
    assert len(calls)==1
    url,kw=calls[0];assert url==ms.ENDPOINT and kw['allow_redirects'] is False
    assert kw['json']['messages'][1]['content']==ms.NOTE
    assert kw['json']['store'] is False and kw['json']['max_completion_tokens']==4096
    assert kw['json']['model']=='muse-spark-1.3'
    grams=ms.candidate_grams(record['candidate'])
    with pytest.raises(ValueError):ms.confirm_stock(record,grams)
    confirmed=ms.confirm_stock(record,grams,confirmed=True)
    result=plan_prep({'pizza-demo':29},RECIPES,confirmed['stock'],60)
    assert result['prepared']['pizza-demo']==20 and result['unmet']['pizza-demo']==9
    assert confirmed['request_id']=='MOCK-TEST-NOT-LIVE'
    grams['cheese']=3500
    corrected=ms.confirm_stock(record,grams,confirmed=True)
    assert corrected['before']['ingredients'][1]['quantity']==2
    assert plan_prep({'pizza-demo':29},RECIPES,corrected['stock'],60)['prepared']['pizza-demo']==29


@pytest.mark.parametrize('change',['quote','duplicate','negative','null'])
def test_bad_or_unresolved_extractions(change):
    c=candidate()
    if change=='quote':c['ingredients'][0]['source_quote']='invented evidence'
    if change=='duplicate':c['ingredients'][1]['ingredient']='dough'
    if change=='negative':c['ingredients'][0]['quantity']=-1
    if change=='null':
        c['ingredients'][0]['quantity']=None
        grams=ms.candidate_grams(c)
        record=dict(mode='live_meta_unconfirmed',source_hash=ms.SOURCE_HASH,source_note=ms.NOTE,candidate=c,request_id='MOCK',model=ms.MODEL)
        with pytest.raises(ValueError):ms.confirm_stock(record,grams,confirmed=True)
    else:
        with pytest.raises(ValueError):ms.validate_candidate(c)


@pytest.mark.parametrize('failure',['refused','truncated','invalid_json','status','timeout'])
def test_failures_never_return_confirmed_stock(monkeypatch,failure):
    authorize(monkeypatch);b=body()
    if failure=='refused':b['choices'][0]['message']['refusal']='declined'
    if failure=='truncated':b['choices'][0]['finish_reason']='length'
    if failure=='invalid_json':b['choices'][0]['message']['content']='broken'
    calls=mock_post(monkeypatch,b,status=401 if failure=='status' else 200)
    if failure=='timeout':
        def fail(*a,**k):raise requests.Timeout()
        monkeypatch.setattr(ms.requests,'post',fail)
    with pytest.raises((ValueError,RuntimeError)):ms.extract_demo_stock(authorized=True)
    assert len(calls)<=1


def test_changed_source_rejects_confirmation(monkeypatch):
    authorize(monkeypatch);mock_post(monkeypatch);r=ms.extract_demo_stock(authorized=True)
    r['source_hash']='stale'
    with pytest.raises(ValueError):ms.confirm_stock(r,{'dough':10000,'cheese':2000,'sauce':3000},confirmed=True)


def test_ui_mocked_flow_and_no_repeat_call(monkeypatch):
    authorize(monkeypatch);calls=mock_post(monkeypatch)
    app=AppTest.from_file(ROOT/'app.py').run(timeout=30)
    app.sidebar.radio[0].set_value('Meta Evidence').run()
    assert calls==[]
    app.checkbox[0].check().run()
    app.button[0].click().run()
    assert len(calls)==1 and app.button[0].disabled
    app.run();assert len(calls)==1
    app.checkbox[1].check()
    next(b for b in app.button if b.label=='Confirm stock for Prep Planner').click().run()
    assert not app.exception
    app.sidebar.radio[0].set_value('Prep Planner').run(timeout=30)
    assert [n.value for n in app.number_input[:3]]==[10000.0,2000.0,3000.0]
    app.checkbox[0].check();app.button[0].click().run()
    assert [m.value for m in app.metric]==['29','20','9','40']
    assert len(calls)==1


def test_default_ui_is_blocked_and_does_not_invent_result(monkeypatch):
    monkeypatch.delenv('MODEL_API_KEY',raising=False)
    monkeypatch.delenv('META_LIVE_ENABLED',raising=False)
    calls=mock_post(monkeypatch)
    app=AppTest.from_file(ROOT/'app.py').run(timeout=30)
    app.sidebar.radio[0].set_value('Meta Evidence').run()
    assert app.button[0].disabled and not app.success
    app.checkbox[0].check().run()
    assert app.button[0].disabled and calls==[]
    assert any('Live verification blocked' in w.value for w in app.warning)
