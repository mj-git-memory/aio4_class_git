print()
from pydantic import BaseModel, ValidationError
from typing import Optional, Union

class Student(BaseModel):
    name: str
    # - 숫자로 변경가능한 문자열 숫자 입력하면 자동으로 숫자로 변환 
    age: int
    interests: list[str]
    # - 선택적으로 입력받는 nickname 필드 추가(기본값은 None)
    nickname: Optional[str] = None # nickname은 문자열이거나 None일 수 있으며, 기본값은 None 
    # nickname: Union[str, None] = None  # <- 이렇게 쓸 수도 있음 
    # - 학번 student_id 필드 추가(수정 또는 문자열 모두 허용)
    student_id: Union[int, str] = None  # 학번은 정수 또는 문자열로 입력 가능, 기본값은 None

## 함수를 정의하는 코드
def main() -> None:
    # 아래 데이터를 문자열 age = '123'으로 바꿔 실행한 뒤 결과 타입 확인
    student = Student(name="하늘", age=23, interests=["AI", "python"])
    student = Student(name="하늘", age=23, interests=["AI", "python"], nickname="Sky", student_id="2024001")
    print('학생 - ', student)
    print('age 타입', type(student.age))
    print('dictionary 변환', student.model_dump())
    # age에 스물셋을 전달하고, ValidationError를 처리하는 코드 작성

## 함수를 실행하는 코드 
if __name__ == "__main__": # .
    main()

