import asyncio
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from config import Config
from typing import Literal

# 환경변수 검증
Config.validate()

async def main(user_query: str = None):
    # MCP 서버 등록: stdio로 로컬 파이썬 스크립트 실행
    client = MultiServerMCPClient({
        "yfinance": {
            "command": "python",
            "args": ["./src/mcp_yfinance_server.py"],
            "transport": "stdio",
        }
    })
    tools = await client.get_tools()

    # 모델 초기화 및 ReAct 에이전트 구성
    model = init_chat_model(Config.LLM_ID)
    agent = create_react_agent(model, tools)

    # 사용자 질의 또는 기본 질의
    if user_query is None:
        user_query = (
            "AAPL 최신 가격을 알려주고, 최근 5일 일봉 OHLC를 요약해줘. "
            "가격과 통화, 거래소도 함께."
        )
    
    result = await agent.ainvoke({
        "messages": [
            {"role": "system", "content": Config.SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ]
    })
    return result["messages"][-1].content

if __name__ == "__main__":
    result = asyncio.run(main())
    print(result)


#  동적으로 페르소나 / 리스크 레벨 바꾸기
def build_prompt(persona: Literal["swing","intraday","position"]="swing",
                 risk: Literal["conservative","balanced","aggressive"]="conservative") -> str:
    base = Config.SYSTEM_PROMPT
    persona_line = {
        "swing": "너는 '스윙 트레이더'로 3일~3주 구간을 중시한다.",
        "intraday": "너는 '당일 트레이더'로 분·기간 단위 신속 판단을 중시한다.",
        "position": "너는 '포지션 트레이더'로 수주~수개월 추세를 중시한다.",
    }[persona]
    risk_line = {
        "conservative": "리스크는 낮게: 손절은 타이트, 포지션은 보수적으로.",
        "balanced": "리스크는 중간: 손절/익절 균형, 포지션 중간.",
        "aggressive": "리스크는 높게: 손절은 넓게 허용 가능하나 근거 필수.",
    }[risk]
    return f"{persona_line}\n{risk_line}\n{base}"