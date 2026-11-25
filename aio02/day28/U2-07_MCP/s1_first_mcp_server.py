# python -m pip install -r requirement.txt
# brew install node --> bash 터미널에서 실행
# python -m pip install uv
# uv run python --version

from mcp.server.mcpserver import MCPServer
mcp = MCPServer("MyHelper")

# 외부에 노출할 도구 정의
@mcp.tool()
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

if __name__ == '__main__' :
    # 기본 전송 방식 stdio로 mcp 서버 실행(클라이언트가 서브 프로세스로 호출)
    mcp.run(transport='stdio')


# mcp dev s1_first_mcp_server.py  # -> 실행 명령어