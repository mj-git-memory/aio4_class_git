## s1은 “MCP 도구를 제공하는 서버”
# s1 실행 구조
# Inspector·Codex 같은 MCP 클라이언트
#     ↓ MCP 도구 호출
# s1: 함수 실행
#     ↓ MCP 결과 응답
# 클라이언트가 결과 확인

# python -m pip install -r requirement.txt
# brew install node --> bash 터미널에서 실행
# python -m pip install uv
# uv run python --version


## s1: MCP 서버를 만들고 도구 제공하기
# 서버 객체 생성
# → 도구 두 개 등록
# → 서버 실행
# → 클라이언트 요청 대기
# → 요청한 함수 실행
# → 결과 응답
from mcp.server.mcpserver import MCPServer
mcp = MCPServer("MyHelper")

# 외부에 노출할 도구 정의
@mcp.tool()  # 	아래 함수를 MCP 도구로 등록
def add_number(a:int, b:int) -> dict:
    '''두 정수 a,b를 더한 결과를 반환'''
    return {'a':a, 'b':b, 'sum':a+b}

@mcp.tool()
def check_server_env(service_name:str) -> dict:
    '''서비스 이름(service_name)의 운영환경과 포트 정보를 조회'''
    envs = {
        'auth':{'env':'prod', 'port':8001}

    }
    key = service_name.lower()
    return {'service':key, **envs.get(key)}

if __name__ == '__main__' :  # 이 파일을 직접 실행했을 때만 아래 코드 실행
    # 기본 전송 방식 stdio로 mcp 서버 실행(클라이언트가 서브 프로세스로 호출)
    mcp.run(transport='stdio') 
    # mcp.run(...): 서버를 실행하고 요청을 기다림 / transport="stdio": 표준 입력·출력으로 MCP 클라이언트와 통신



# mcp dev s1_first_mcp_server.py --with "mcp[cli]==2.3.0" --with httpx   # -> 실행 명령어