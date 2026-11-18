import json
import pytest
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from app.catalog import read_catalog, find_product, product_context, DEFAULT_DATA, data_info
from app.config import Settings
from app.providers import make_model
from app.prompts import get_prompt
from app.pipeline import prepare_input, build_chain, sample_requests
from app.report import save_report


def test_bundled_data_has_twenty_records():
    records=read_catalog(); assert len(records)==20
    assert records[0]["record_id"]=="row-001"
    assert records[0]["title"].startswith("Fjallraven")

def test_price_and_unverified_fields_excluded():
    text=product_context(read_catalog()[0]); value=json.loads(text)
    assert set(value)=={"record_id","title","category","description"}
    assert "price" not in value and "rating" not in value

@pytest.mark.parametrize("question",["","  ",None,5,"가"*501])
def test_invalid_question(question):
    with pytest.raises(ValueError): prepare_input({"record_id":"row-001","question":question},read_catalog())

def test_untrusted_context_not_used():
    value=prepare_input({"record_id":"row-001","question":"  질문 {x}  ","context":"재고100개"},read_catalog())
    assert value["question"]=="질문 {x}" and "재고100개" not in value["context"]

def test_non_dict_rejected():
    with pytest.raises(TypeError):prepare_input("질문",read_catalog())

def test_unknown_id_rejected():
    with pytest.raises(ValueError):find_product(read_catalog(),"row-999")

def test_missing_variable():
    with pytest.raises(KeyError):get_prompt().invoke({"question":"질문"})

def test_same_context_all_versions():
    values=prepare_input(sample_requests(read_catalog())[0],read_catalog())
    for version in ("weak","role","designed"):
        assert values["context"] in get_prompt(version).invoke(values).to_string()

def test_parser_does_not_check_facts():
    assert StrOutputParser().invoke(AIMessage(content="현재 재고100개"))=="현재 재고100개"

def test_real_lcel_with_mock():
    records=read_catalog(); chain=build_chain(make_model(Settings("mock","local-fixture")),records)
    assert "[모의 응답]" in chain.invoke(sample_requests(records)[0])

def test_batch_failure_and_stream():
    records=read_catalog(); chain=build_chain(make_model(Settings("mock","local-fixture")),records)
    request=sample_requests(records)[0]
    out=chain.batch([request,{**request,"question":""}],config={"max_concurrency":1},return_exceptions=True)
    assert isinstance(out[1],ValueError)
    assert "".join(chain.stream(request))==out[0]

@pytest.mark.parametrize("value",[{},[],[{"title":"x"}],[None]])
def test_catalog_invalid(tmp_path,value):
    path=tmp_path/'bad.json';path.write_text(json.dumps(value))
    with pytest.raises(ValueError):read_catalog(path)

def test_source_mode_and_hash():
    info=data_info(); assert info["acquisition"]=="public_derived_file"
    assert len(info["sha256"])==64


def test_api_id_mapping_and_duplicate_rejection(tmp_path):
    rows=[{'id':1,'title':'A','category':'C','description':'D'}]
    path=tmp_path/'api.json';path.write_text(json.dumps(rows))
    assert read_catalog(path)[0]['record_id']=='api-1'
    path.write_text(json.dumps(rows*2))
    with pytest.raises(ValueError,match='중복'):read_catalog(path)


def test_report_escapes_untrusted_text_and_preserves_modes(tmp_path,monkeypatch):
    import app.report as report
    monkeypatch.setattr(report,'ROOT',tmp_path)
    records=read_catalog()
    row={'record_id':records[0]['record_id'],'question':'<script>alert(1)</script>','answer':'<img src=x>','status':'ok'}
    path=report.save_report(8,records,[row],DEFAULT_DATA,Settings('mock','local-fixture'))
    html=path.read_text()
    assert '<script>' not in html and '&lt;script&gt;' in html
    payload=json.loads(path.with_suffix('.json').read_text())
    assert payload['data']['acquisition']=='public_derived_file'
    assert payload['provider']=='mock'
    assert payload['rows'][0]['question']==row['question']


def test_report_without_model_is_labeled(tmp_path,monkeypatch):
    import app.report as report
    monkeypatch.setattr(report,'ROOT',tmp_path)
    path=report.save_report(1,read_catalog(),[],DEFAULT_DATA)
    payload=json.loads(path.with_suffix('.json').read_text())
    assert payload['model_mode']=='모델 호출 없음'
