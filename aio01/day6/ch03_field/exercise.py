from pydantic import BaseModel, Field, ValidationError


class Product(BaseModel) :
    # - To Do - title: 최소 2자, 최대 60자
    title : str = Field(min_length=2, max_length=60)
    # - To Do - price: 0보다 커야 함
    price : int = Field(gt=0)
    # - To Do - stock: 0 이상, 기본값 0
    stock : int = Field(ge=0, default=0)
    # - To Do - sku: SKU-와 숫자 네 자리 패턴
    sku : str = Field(pattern= r'^SKU-[0-9]{4}$') 
    # pass

def main() -> None:
    print('To Do: 정상 상품 및 잘못된 상품을 테스트하세요.')
    try : 
        # test_prd1 = Product(title='사과', price = 0, sku = 'SKU-0001')  # error : 1 validation error for Product
        # test_prd2 = Product(price = 0, sku = 'SKU-001') # error :  3 validation errors for Product
        test_prd3 = Product(title='사과', sku = 'SKU-0010') # error : 1 validation error for Product

        # data = Product.model_validate(test_prd1) 
        # data = Product.model_validate(test_prd2) 
        data = Product.model_validate(test_prd3) 
        print(data)
        print('---')

    except ValidationError as er :
        print('error : ', er)
        print('---')
        print('error : ', er.errors()[0]) 
        # test_prd1 -> error :  {'type': 'greater_than', 'loc': ('price',), 'msg': 'Input should be greater than 0', 'input': 0, 'ctx': {'gt': 0}, 'url':'https://errors.pydantic.dev/2.14/v/greater_than'}
        # test_prd2 -> error :  {'type': 'missing', 'loc': ('title',), 'msg': 'Field required', 'input': {'price': 0, 'sku': 'SKU-001'}, 'url': 'https://errors.pydantic.dev/2.14/v/missing'}
        # test_prd3 -> error :  {'type': 'missing', 'loc': ('price',), 'msg': 'Field required', 'input': {'title': '사과', 'sku': 'SKU-0010'}, 'url': 'https://errors.pydantic.dev/2.14/v/missing'}

if __name__ == '__main__':
    main()


print('---------------------')
class Product(BaseModel):
    title: str = Field(min_length=2, max_length=60)
    price: int = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    sku: str = Field(pattern=r'^SKU-[0-9]{4}$')

def main() -> None:
    product = Product(title='키보드', price=50000, sku='SKU-0001')
    print('검증 성공:', product.model_dump(),' ', type(product.model_dump()))
    print('검증 성공:', product, ' ', type(product))
    print('---')

    invalid_cases = [
        {'title': 'A'},
        {'title': 'A' * 61},
        {'price': 0},
        {'stock': -1, 'title': 'A'},
        {'sku': 'SKU-001'},
    ]
    for changes in invalid_cases:
        data = product.model_dump()
        data.update(changes)

        try:
            Product(**data)
        except ValidationError as error:
            print('검증 실패:', changes)
            for detail in error.errors():
                print(detail['loc'], detail['type'])
        else:
            raise AssertionError(f'잘못된 입력이 검증을 통과했습니다: {changes}')
        print('---')


if __name__ == '__main__':
    main()