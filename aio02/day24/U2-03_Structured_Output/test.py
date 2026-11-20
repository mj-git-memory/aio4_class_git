# from pathlib import Path
# import csv
# ROOT = Path(__file__).resolve().parent
# FILES = {"bank": "bank.csv", "product": "fakestore_products.json"}
# dataset = 'bank'
# path = ROOT / "data" / FILES[dataset]
# with path.open(encoding="utf-8-sig", newline="") as stream:        
#         result = list(csv.DictReader(stream, delimiter=";"))

# print(result[0])

#########
from pydantic import BaseModel, ConfigDict, ValidationError

class MyClass(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    name :str
    age : int

print(MyClass.model_json_schema())     #####
obj = MyClass(name='abc',age=22)

obj_model_dump = obj.model_dump()  #####

del obj_model_dump['name']
print(obj_model_dump)

try:

    MyClass.model_validate(obj_model_dump)  #####

except ValueError as err:
    print(err.errors())    

# print( obj.model_dump())