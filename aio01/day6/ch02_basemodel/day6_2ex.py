from pydantic import BaseModel, ValidationError

# - To Do : Book 모델의 필드 정의
# title : str(필수), price:int(필수), in_stock:bool=True, note:str|None=None

class Book(BaseModel) : 
    title : str
    price : int
    in_stock : bool = True
    note : str | None = None

def main() -> None : 
    # - To Do : Book(title='파이썬 기초', price = '19000') 만들기
    book1 = Book(title = '파이썬 기초', price = '19000')
    # - To Do : model_dump() 호출, 가격이 int로 변환되었는지 확인
    # model_dump()를 호출하면 딕셔너리가 반환
    book1_dict = book1.model_dump()
    print(book1_dict)
    print(type(book1_dict['price']))
    print('---')
    # - To Do : title 누락 시 ValidationError 확인 
    try : 
        book2 = Book(price=1000)
    except ValidationError as er : 
        print('에러 :', er)
        print('에러 :', er.errors()[0])
    # print('To Do를 완성하세요')

if __name__ == '__main__' :
    main()