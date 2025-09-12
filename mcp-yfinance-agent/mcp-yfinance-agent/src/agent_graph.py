import asyncio
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from config import Config
from typing import Literal, Dict, Any, Optional
from memory_manager import memory_manager
from personalized_analyzer import PersonalizedStockAnalyzer, BuySellRecommendationEngine
from investment_profile import InvestmentProfile

# 환경변수 검증
Config.validate()

class InvestmentAgent:
    """투자 성향 기반 AI 에이전트"""
    
    def __init__(self):
        self.analyzer = PersonalizedStockAnalyzer()
        self.recommendation_engine = BuySellRecommendationEngine()
        self.client = None
        self.agent = None
        self.model = None
    
    async def initialize(self):
        """에이전트 초기화"""
        # MCP 서버 등록: stdio로 로컬 파이썬 스크립트 실행
        self.client = MultiServerMCPClient({
            "yfinance": {
                "command": "python",
                "args": ["./src/mcp_yfinance_server.py"],
                "transport": "stdio",
            }
        })
        tools = await self.client.get_tools()

        # 모델 초기화 및 ReAct 에이전트 구성
        self.model = init_chat_model(Config.LLM_ID)
        self.agent = create_react_agent(self.model, tools)
    
    async def process_query(self, user_query: str, user_id: str = "default_user") -> Dict[str, Any]:
        """사용자 쿼리 처리"""
        if not self.agent:
            await self.initialize()
        
        # 사용자 메모리 가져오기
        memory = memory_manager.get_memory(user_id)
        memory.add_message("user", user_query)
        
        # 투자 성향 프로필 확인
        profile = memory_manager.get_user_profile(user_id)
        
        if not profile:
            # 투자 성향 수집 시작
            return await self._start_profile_collection(user_id)
        
        # 투자 성향 기반 분석 수행
        return await self._analyze_with_profile(user_query, user_id, profile)
    
    async def _start_profile_collection(self, user_id: str) -> Dict[str, Any]:
        """투자 성향 수집 시작"""
        result = memory_manager.start_profile_collection(user_id)
        
        memory = memory_manager.get_memory(user_id)
        memory.add_message("system", "투자 성향을 파악하기 위해 몇 가지 질문을 드리겠습니다.")
        
        return {
            "type": "profile_collection",
            "message": "투자 성향을 파악하기 위해 몇 가지 질문을 드리겠습니다.",
            "question": result["first_question"],
            "requires_user_input": True
        }
    
    async def _analyze_with_profile(self, user_query: str, user_id: str, 
                                  profile: InvestmentProfile) -> Dict[str, Any]:
        """투자 성향 기반 분석"""
        # 종목 추출 (간단한 패턴 매칭)
        ticker = self._extract_ticker(user_query)
        
        if ticker:
            # 종목 분석 및 추천
            analysis = self.analyzer.analyze_stock(ticker, user_id)
            if analysis:
                recommendation = self.recommendation_engine.get_recommendation(ticker, user_id)
                
                # 맞춤형 시스템 프롬프트 생성
                personalized_prompt = self._build_personalized_prompt(profile, analysis, recommendation)
                
                # 에이전트 실행
                result = await self.agent.ainvoke({
                    "messages": [
                        {"role": "system", "content": personalized_prompt},
                        {"role": "user", "content": user_query},
                    ]
                })
                
                memory = memory_manager.get_memory(user_id)
                memory.add_message("assistant", result["messages"][-1].content)
                
                return {
                    "type": "analysis",
                    "content": result["messages"][-1].content,
                    "analysis": analysis,
                    "recommendation": recommendation,
                    "profile": profile
                }
        
        # 일반적인 주식 정보 조회
        result = await self.agent.ainvoke({
            "messages": [
                {"role": "system", "content": self._build_general_prompt(profile)},
                {"role": "user", "content": user_query},
            ]
        })
        
        memory = memory_manager.get_memory(user_id)
        memory.add_message("assistant", result["messages"][-1].content)
        
        return {
            "type": "general",
            "content": result["messages"][-1].content,
            "profile": profile
        }
    
    def _extract_ticker(self, query: str) -> Optional[str]:
        """쿼리에서 종목 코드 추출"""
        import re
        
        # 일반적인 종목 코드 패턴
        patterns = [
            r'\b([A-Z]{1,5})\b',  # 대문자 1-5자
            r'\$([A-Z]{1,5})\b',  # $AAPL 형태
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query.upper())
            if matches:
                # 일반적인 종목 코드 필터링
                common_tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
                for match in matches:
                    if match in common_tickers or len(match) <= 5:
                        return match
        
        return None
    
    def _build_personalized_prompt(self, profile: InvestmentProfile, 
                                 analysis, recommendation) -> str:
        """맞춤형 시스템 프롬프트 생성"""
        base_prompt = Config.SYSTEM_PROMPT
        
        profile_info = f"""
사용자 투자 성향:
- 리스크 성향: {profile.risk_tolerance.value}
- 투자 기간: {profile.investment_horizon.value}
- 거래 스타일: {profile.trading_style.value}
- 선호 섹터: {', '.join(profile.preferred_sectors) if profile.preferred_sectors else '없음'}
- 최대 포지션 크기: {profile.max_position_size}%
- 손절매 허용 범위: {profile.stop_loss_tolerance}%
- 익절 목표: {profile.take_profit_target}%

종목 분석 결과:
- 현재가: ${analysis.current_price:.2f} {analysis.currency}
- 종합 점수: {analysis.overall_score:.1f}/100
- 리스크 점수: {analysis.risk_score:.1f}/100
- 모멘텀 점수: {analysis.momentum_score:.1f}/100
- 추세 점수: {analysis.trend_score:.1f}/100

추천 결과:
- 추천 액션: {recommendation['recommendation']}
- 신뢰도: {recommendation['confidence']}%
- 매수 가격 범위: ${recommendation['buy_price_range']['lower']:.2f} - ${recommendation['buy_price_range']['upper']:.2f}
- 매도 가격 범위: ${recommendation['sell_price_range']['lower']:.2f} - ${recommendation['sell_price_range']['upper']:.2f}
- 손절매: ${recommendation['stop_loss']:.2f}
- 익절매: ${recommendation['take_profit']:.2f}
"""
        
        return f"{base_prompt}\n\n{profile_info}\n\n위 정보를 바탕으로 사용자의 투자 성향에 맞는 맞춤형 조언을 제공하세요."
    
    def _build_general_prompt(self, profile: InvestmentProfile) -> str:
        """일반적인 시스템 프롬프트 생성"""
        base_prompt = Config.SYSTEM_PROMPT
        
        profile_info = f"""
사용자 투자 성향:
- 리스크 성향: {profile.risk_tolerance.value}
- 투자 기간: {profile.investment_horizon.value}
- 거래 스타일: {profile.trading_style.value}
- 선호 섹터: {', '.join(profile.preferred_sectors) if profile.preferred_sectors else '없음'}
"""
        
        return f"{base_prompt}\n\n{profile_info}\n\n사용자의 투자 성향을 고려하여 조언을 제공하세요."

# 전역 에이전트 인스턴스
investment_agent = InvestmentAgent()

async def main(user_query: str = None, user_id: str = "default_user"):
    """메인 함수"""
    result = await investment_agent.process_query(user_query or "AAPL 분석해줘", user_id)
    return result

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