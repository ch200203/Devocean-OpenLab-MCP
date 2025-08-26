from __future__ import annotations
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import asyncio
from agent_graph import main as run_agent
from config import Config

mcp = FastMCP("StockAgent")

class AgentRequest(BaseModel):
    query: str
    max_iterations: int = 10

class AgentResponse(BaseModel):
    result: str
    success: bool
    error: str | None = None

@mcp.tool()
async def ask_stock_agent(query: str, max_iterations: int = 10) -> AgentResponse:
    """
    주식 시세 조회 AI 에이전트에게 질문을 합니다.
    
    Args:
        query: 주식 관련 질문 (예: "AAPL 최신 가격을 알려주고, 최근 5일 일봉 OHLC를 요약해줘")
        max_iterations: 최대 반복 횟수 (기본값: 10)
    
    Returns:
        AgentResponse: 에이전트의 응답 결과
    """
    try:
        # 에이전트 실행을 위한 설정
        Config.AGENT_MAX_ITERATIONS = max_iterations
        
        # 에이전트 실행
        result = await run_agent(query)
        
        return AgentResponse(
            result=result,
            success=True,
            error=None
        )
    except Exception as e:
        return AgentResponse(
            result="",
            success=False,
            error=str(e)
        )

@mcp.tool()
def get_agent_info() -> Dict[str, Any]:
    """
    AI 에이전트의 정보를 반환합니다.
    """
    return {
        "name": "Stock Market AI Agent",
        "description": "Yahoo Finance를 통해 주식 시세 정보를 조회하는 AI 에이전트",
        "capabilities": [
            "실시간 주식 가격 조회",
            "주식 히스토리 데이터 조회",
            "OHLCV 데이터 분석",
            "자연어 질의 응답"
        ],
        "config": {
            "llm_id": Config.LLM_ID,
            "max_iterations": Config.AGENT_MAX_ITERATIONS,
            "verbose": Config.AGENT_VERBOSE
        }
    }

if __name__ == "__main__":
    # 표준 입출력(stdio) 트랜스포트로 실행
    mcp.run(transport="stdio")