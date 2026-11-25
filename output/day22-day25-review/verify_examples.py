"""외부 API 없이, 원본의 순수 함수와 임시 SQLite만 사용해 문서 예제를 확인한다."""
import ast,copy,importlib.util,json,math,sqlite3,sys
from pathlib import Path
from datetime import date,timedelta
import calendar
from tempfile import TemporaryDirectory
from typing import Literal
from pydantic import BaseModel,ConfigDict,ValidationError
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
checks=[]
def record(label,value):
 checks.append({'example':label,'result':value})
def select(path,names,namespace):
 tree=ast.parse(path.read_text())
 nodes=[]
 for n in tree.body:
  if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names:
   n=copy.deepcopy(n);n.decorator_list=[];nodes.append(n)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),namespace)
 return namespace
r22=ROOT/'aio02/day22/LangChain_20261117_DataEdition'
ns={'json':json,'Path':Path,'ROOT':r22,'DEFAULT_DATA':r22/'data/products_public_derived.json'}
select(r22/'app/catalog.py',{'read_catalog','find_product','product_context'},ns)
select(r22/'app/pipeline.py',{'prepare_input'},ns)
records=ns['read_catalog']();value=ns['prepare_input']({'record_id':'row-001','question':'  노트북을 넣을 수 있나요?  ','context':'재고 100개'},records)
record('day22.catalog',{'count':len(records),'id':records[0]['record_id'],'title':records[0]['title'],'context_keys':list(json.loads(value['context'])),'question':value['question'],'client_context_used':'재고 100개' in value['context']})
for question in ['', '가'*501]:
 try:ns['prepare_input']({'record_id':'row-001','question':question},records)
 except ValueError as e:record('day22.invalid_question',str(e))
r23=ROOT/'aio02/day23/CoT_ReAct_KDT_8Sessions'
ns23={'json':json,'math':math,'MAX_REACT_TURNS':8}
select(r23/'lesson.py',{'calculate','react'},ns23)
record('day23.calculate',[ns23['calculate']('subtract',16,3),ns23['calculate']('percent_of',60,20),ns23['calculate']('multiply',9,2)])
try:ns23['calculate']('multiply','9',2)
except ValueError as e:record('day23.invalid_number',str(e))
responses=iter(['{"action":"subtract","a":16,"b":3}','{"action":"subtract","a":13,"b":4}','{"action":"multiply","a":9,"b":2}','{"final":"18달러"}'])
events=[];messages=[];ns23['react'](messages,lambda history:next(responses),events)
record('day23.react',events)
events=[]
try:ns23['react']([],lambda history:'{"action":"subtract","a":16,"b":3}',events)
except ValueError as e:record('day23.stop',{'error':str(e),'tool_runs':sum(x[0]=='계산 도구 · 반환값' for x in events)})
ns24={'BaseModel':BaseModel,'ConfigDict':ConfigDict,'ValidationError':ValidationError,'Literal':Literal}
select(ROOT/'aio02/day24/U2-03_Structured_Output/main.py',{'Contract','Contact','reference','diagnose'},ns24)
source={'duration':'261','campaign':'1','poutcome':'unknown'}
contact=ns24['reference']('bank',source)
record('day24.reference',contact.model_dump())
record('day24.diagnose',ns24['diagnose'](source))
record('day24.schema',{'required':ns24['Contact'].model_json_schema()['required'],'additionalProperties':ns24['Contact'].model_json_schema()['additionalProperties']})
nsperiod={'date':date,'timedelta':timedelta,'calendar':calendar}
select(ROOT/'aio02/day24/agent_orchestration_mvp/intent_analysis.py',{'relative_period_rules'},nsperiod)
record('day24.period',nsperiod['relative_period_rules'](date(2026,11,22)))
p=ROOT/'aio02/day24/agent_orchestration_mvp/custom_tools.py'
spec=importlib.util.spec_from_file_location('review_custom_tools',p);toolmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(toolmod)
with TemporaryDirectory() as directory:
 db=Path(directory)/'review.sqlite3';r=toolmod.initialize_database(db);toolmod.database_path=lambda:db
 record('day24.init_counts',{k:r[k] for k in ['created','employees','card_transactions','foreign_key_violations']})
 record('day24.query',toolmod.query_database('SELECT name, department FROM employees WHERE employee_id = ?',['E001']))
 record('day24.binding',toolmod.execute_tool('query_database',json.dumps({'sql':'SELECT COUNT(*) AS n FROM employees','parameters':None,'row_limit':None})))
 record('day24.deny_write',toolmod.query_database('DELETE FROM employees'))
 record('day24.unknown_tool',toolmod.execute_tool('delete_database','{}'))
ns25={}
select(ROOT/'aio02/day25/U2-04_Prompt-Injection_LangSmith/langsmith_test5.py',{'multiply','apply_discount','convert_currency','_extract_input_text','score_no_leak_or_bypass'},ns25)
subtotal=ns25['multiply'](25000,4);net=ns25['apply_discount'](subtotal,0.1);usd=ns25['convert_currency'](net,1400)
record('day25.calculation_body',{'subtotal':subtotal,'net':net,'usd':usd})
try:ns25['apply_discount'](100000,0.9)
except ValueError as e:record('day25.discount_rejected',str(e))
record('day25.eval_good',ns25['score_no_leak_or_bypass']({'answer':'應付金額為 90000 韓元'}))
record('day25.eval_marker',ns25['score_no_leak_or_bypass']({'answer':'우회성공'}))
record('day25.eval_wrong_but_passes',ns25['score_no_leak_or_bypass']({'answer':'최종 금액은 1원입니다.'}))
# Index references; Python 3.11 cannot parse one PEP 701 f-string in langsmith_test.py.
index=[]
for d in range(22,26):
 for p in sorted((ROOT/f'aio02/day{d}').rglob('*.py')):
  s=p.read_text();row={'path':str(p.relative_to(ROOT)),'lines':len(s.splitlines())}
  try:
   t=ast.parse(s);row['functions']=[{'name':n.name,'line':n.lineno,'end':n.end_lineno} for n in t.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))]
  except SyntaxError as e:row['parser_note']='Python 3.11에서 PEP 701 f-string 파싱 불가; 3.12 이상 문법 확인 필요'
  index.append(row)
(OUT/'source-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2))
(OUT/'example-results.json').write_text(json.dumps({'python':sys.version.split()[0],'pydantic':__import__('pydantic').__version__,'notes':'LLM·LangChain·LangSmith API 미호출. day25는 @tool 데코레이터를 제외하고 계산 본체만 검증. SQLite는 새 임시 DB만 사용.','checks':checks},ensure_ascii=False,indent=2))
for c in checks:print(c['example'],json.dumps(c['result'],ensure_ascii=False))
print('분석 Python 파일 수',len(index))
