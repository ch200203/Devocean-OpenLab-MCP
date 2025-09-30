from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import asyncio
from agent_graph import investment_agent
from config import Config
from memory_manager import memory_manager
from investment_profile import InvestmentProfile, RiskTolerance, InvestmentHorizon, TradingStyle
from portfolio_manager import portfolio_manager
from portfolio_analyzer import portfolio_analyzer

mcp = FastMCP("StockAgent")

@dataclass
class AgentRequest(BaseModel):
    query: str
    user_id: str = "default_user"
    max_iterations: int = 10

@dataclass
class AgentResponse(BaseModel):
    result: str
    success: bool
    error: str | None = None
    response_type: str | None = None
    requires_user_input: bool = False
    question: Dict[str, Any] | None = None

@dataclass
class ProfileAnswerRequest(BaseModel):
    user_id: str
    step: str
    answer: str

@dataclass
class ProfileAnswerResponse(BaseModel):
    success: bool
    message: str
    next_question: Dict[str, Any] | None = None
    profile_completed: bool = False
    profile_summary: Dict[str, Any] | None = None
    error: str | None = None

@dataclass
class PortfolioResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any] | None = None
    error: str | None = None

@mcp.tool()
async def ask_stock_agent(query: str, user_id: str = "default_user", max_iterations: int = 10) -> AgentResponse:
    """
    투자 성향 기반 주식 분석 AI 에이전트에게 질문을 합니다.
    
    Args:
        query: 주식 관련 질문 (예: "AAPL 분석해줘", "TSLA 매수 추천해줘")
        user_id: 사용자 ID (기본값: "default_user")
        max_iterations: 최대 반복 횟수 (기본값: 10)
    
    Returns:
        AgentResponse: 에이전트의 응답 결과
    """
    try:
        # 에이전트 실행을 위한 설정
        Config.AGENT_MAX_ITERATIONS = max_iterations
        
        # 에이전트 실행
        result = await investment_agent.process_query(query, user_id)
        
        if result["type"] == "profile_collection":
            return AgentResponse(
                result=result["message"],
                success=True,
                error=None,
                response_type="profile_collection",
                requires_user_input=True,
                question=result["question"]
            )
        elif result["type"] == "analysis":
            return AgentResponse(
                result=result["content"],
                success=True,
                error=None,
                response_type="analysis"
            )
        else:  # general
            return AgentResponse(
                result=result["content"],
                success=True,
                error=None,
                response_type="general"
            )
        
    except Exception as e:
        return AgentResponse(
            result="",
            success=False,
            error=str(e)
        )

@mcp.tool()
async def answer_profile_question(user_id: str, step: str, answer: str) -> ProfileAnswerResponse:
    """
    투자 성향 설문 답변을 처리합니다.
    
    Args:
        user_id: 사용자 ID
        step: 질문 단계 (risk_tolerance, investment_horizon, trading_style, sectors)
        answer: 사용자 답변
    
    Returns:
        ProfileAnswerResponse: 답변 처리 결과
    """
    try:
        result = memory_manager.process_profile_answer(user_id, step, answer)
        
        if result["success"]:
            if result.get("profile_completed"):
                return ProfileAnswerResponse(
                    success=True,
                    message=result["message"],
                    profile_completed=True,
                    profile_summary=result["profile_summary"]
                )
            else:
                return ProfileAnswerResponse(
                    success=True,
                    message="답변이 저장되었습니다.",
                    next_question=result["next_question"]
                )
        else:
            return ProfileAnswerResponse(
                success=False,
                error=result["error"]
            )
            
    except Exception as e:
        return ProfileAnswerResponse(
            success=False,
            error=str(e)
        )

@mcp.tool()
def get_user_profile(user_id: str = "default_user") -> Dict[str, Any]:
    """
    사용자의 투자 성향 프로필을 조회합니다.
    
    Args:
        user_id: 사용자 ID (기본값: "default_user")
    
    Returns:
        Dict: 사용자 프로필 정보
    """
    try:
        profile = memory_manager.get_user_profile(user_id)
        if profile:
            return {
                "user_id": profile.user_id,
                "risk_tolerance": profile.risk_tolerance.value,
                "investment_horizon": profile.investment_horizon.value,
                "trading_style": profile.trading_style.value,
                "preferred_sectors": profile.preferred_sectors,
                "max_position_size": profile.max_position_size,
                "stop_loss_tolerance": profile.stop_loss_tolerance,
                "take_profit_target": profile.take_profit_target,
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat()
            }
        else:
            return {"error": "프로필이 없습니다."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def start_profile_collection(user_id: str = "default_user") -> Dict[str, Any]:
    """
    투자 성향 수집을 시작합니다.
    
    Args:
        user_id: 사용자 ID (기본값: "default_user")
    
    Returns:
        Dict: 첫 번째 질문 정보
    """
    try:
        result = memory_manager.start_profile_collection(user_id)
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def add_position(user_id: str, ticker: str, quantity: float, average_price: float, 
                currency: str = "USD", sector: str = "") -> PortfolioResponse:
    """
    포트폴리오에 포지션을 추가합니다.
    
    Args:
        user_id: 사용자 ID
        ticker: 종목 코드 (예: AAPL, TSLA)
        quantity: 보유 수량
        average_price: 평단가
        currency: 통화 (기본값: USD)
        sector: 섹터 (선택사항)
    
    Returns:
        PortfolioResponse: 포지션 추가 결과
    """
    try:
        position = portfolio_manager.add_position(user_id, ticker, quantity, average_price, currency, sector)
        return PortfolioResponse(
            success=True,
            message=f"{ticker} 포지션이 성공적으로 추가되었습니다.",
            data={
                "ticker": ticker,
                "quantity": position.quantity,
                "average_price": position.average_price,
                "market_value": position.market_value,
                "sector": position.sector
            }
        )
    except Exception as e:
        return PortfolioResponse(
            success=False,
            error=str(e)
        )

@mcp.tool()
def remove_position(user_id: str, ticker: str) -> PortfolioResponse:
    """
    포트폴리오에서 포지션을 제거합니다.
    
    Args:
        user_id: 사용자 ID
        ticker: 종목 코드
    
    Returns:
        PortfolioResponse: 포지션 제거 결과
    """
    try:
        position = portfolio_manager.remove_position(user_id, ticker)
        if position:
            return PortfolioResponse(
                success=True,
                message=f"{ticker} 포지션이 성공적으로 제거되었습니다.",
                data={
                    "ticker": ticker,
                    "final_pnl": position.unrealized_pnl,
                    "final_pnl_percent": position.unrealized_pnl_percent
                }
            )
        else:
            return PortfolioResponse(
                success=False,
                error=f"{ticker} 포지션을 찾을 수 없습니다."
            )
    except Exception as e:
        return PortfolioResponse(
            success=False,
            error=str(e)
        )

@mcp.tool()
def get_portfolio_summary(user_id: str) -> PortfolioResponse:
    """
    포트폴리오 요약 정보를 조회합니다.
    
    Args:
        user_id: 사용자 ID
    
    Returns:
        PortfolioResponse: 포트폴리오 요약
    """
    try:
        summary = portfolio_manager.get_portfolio_summary(user_id)
        return PortfolioResponse(
            success=True,
            message="포트폴리오 요약을 조회했습니다.",
            data=summary
        )
    except Exception as e:
        return PortfolioResponse(
            success=False,
            error=str(e)
        )

@mcp.tool()
def get_positions_list(user_id: str) -> PortfolioResponse:
    """
    포트폴리오의 모든 포지션 목록을 조회합니다.
    
    Args:
        user_id: 사용자 ID
    
    Returns:
        PortfolioResponse: 포지션 목록
    """
    try:
        positions = portfolio_manager.get_positions_list(user_id)
        return PortfolioResponse(
            success=True,
            message=f"{len(positions)}개의 포지션을 조회했습니다.",
            data={"positions": positions}
        )
    except Exception as e:
        return PortfolioResponse(
            success=False,
            error=str(e)
        )

@mcp.tool()
def analyze_portfolio(user_id: str) -> PortfolioResponse:
    """
    포트폴리오를 종합 분석합니다.
    
    Args:
        user_id: 사용자 ID
    
    Returns:
        PortfolioResponse: 포트폴리오 분석 결과
    """
    try:
        profile = memory_manager.get_user_profile(user_id)
        analysis = portfolio_analyzer.analyze_portfolio(user_id, profile)
        
        return PortfolioResponse(
            success=True,
            message="포트폴리오 분석이 완료되었습니다.",
            data={
                "total_invested": analysis.total_invested,
                "total_market_value": analysis.total_market_value,
                "total_unrealized_pnl": analysis.total_unrealized_pnl,
                "total_unrealized_pnl_percent": analysis.total_unrealized_pnl_percent,
                "sector_allocation": analysis.sector_allocation,
                "risk_metrics": analysis.risk_metrics,
                "performance_metrics": analysis.performance_metrics,
                "recommendations": analysis.recommendations,
                "positions_analysis": analysis.positions_analysis,
                "last_updated": analysis.last_updated.isoformat()
            }
        )
    except Exception as e:
        return PortfolioResponse(
            success=False,
            error=str(e)
        )

@mcp.tool()
def get_position_recommendation(user_id: str, ticker: str) -> PortfolioResponse:
    """
    특정 포지션에 대한 추천을 조회합니다.
    
    Args:
        user_id: 사용자 ID
        ticker: 종목 코드
    
    Returns:
        PortfolioResponse: 포지션 추천
    """
    try:
        profile = memory_manager.get_user_profile(user_id)
        recommendation = portfolio_analyzer.get_position_recommendation(user_id, ticker, profile)
        
        if recommendation:
            return PortfolioResponse(
                success=True,
                message=f"{ticker} 포지션 추천을 조회했습니다.",
                data={
                    "ticker": ticker,
                    "current_position": {
                        "quantity": recommendation.current_position.quantity,
                        "average_price": recommendation.current_position.average_price,
                        "current_price": recommendation.current_position.current_price,
                        "unrealized_pnl": recommendation.current_position.unrealized_pnl,
                        "unrealized_pnl_percent": recommendation.current_position.unrealized_pnl_percent
                    },
                    "stock_analysis": {
                        "overall_score": recommendation.stock_analysis.overall_score,
                        "risk_score": recommendation.stock_analysis.risk_score,
                        "momentum_score": recommendation.stock_analysis.momentum_score,
                        "trend_score": recommendation.stock_analysis.trend_score
                    },
                    "recommendation": {
                        "action": recommendation.recommendation,
                        "confidence": recommendation.confidence,
                        "reasoning": recommendation.reasoning,
                        "target_price": recommendation.target_price,
                        "stop_loss": recommendation.stop_loss,
                        "take_profit": recommendation.take_profit
                    }
                }
            )
        else:
            return PortfolioResponse(
                success=False,
                error=f"{ticker} 포지션을 찾을 수 없습니다."
            )
    except Exception as e:
        return PortfolioResponse(
            success=False,
            error=str(e)
        )

@mcp.tool()
def get_agent_info() -> Dict[str, Any]:
    """
    AI 에이전트의 정보를 반환합니다.
    """
    return {
        "name": "Personalized Stock Investment AI Agent",
        "description": "투자 성향 기반 맞춤형 주식 분석 및 추천 AI 에이전트",
        "capabilities": [
            "투자 성향 설문 및 프로필 관리",
            "투자 성향 기반 맞춤형 종목 분석",
            "매수/매도 라인 추천",
            "포트폴리오 추적 및 관리",
            "포트폴리오 기반 분석 및 추천",
            "기술적 지표 분석",
            "리스크 관리 조언",
            "실시간 주식 가격 조회",
            "주식 히스토리 데이터 조회",
            "OHLCV 데이터 분석",
            "자연어 질의 응답"
        ],
        "features": [
            "보수적/중간/공격적 리스크 성향 지원",
            "단기/중기/장기 투자 기간 지원",
            "당일/스윙/포지션/가치 투자 스타일 지원",
            "섹터별 선호도 반영",
            "개인화된 손절/익절 가이드라인",
            "대화형 투자 성향 수집",
            "포트폴리오 추적 및 수익률 계산",
            "포지션별 맞춤형 추천",
            "포트폴리오 리스크 분석"
        ],
        "portfolio_tools": [
            "add_position - 포지션 추가",
            "remove_position - 포지션 제거",
            "get_portfolio_summary - 포트폴리오 요약",
            "get_positions_list - 포지션 목록",
            "analyze_portfolio - 포트폴리오 분석",
            "get_position_recommendation - 포지션 추천"
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