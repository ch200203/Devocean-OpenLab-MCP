#!/usr/bin/env python3
"""
A2A 연동 통합 모듈
기존 에이전트들을 A2A 프로토콜과 연동하여 다른 AI 에이전트들과 협업할 수 있도록 함
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from a2a_protocol import (
    AgentCapability, AgentRole, A2AProtocol,
    StockAnalysisRequest, StockAnalysisResponse,
    PortfolioAnalysisRequest, PortfolioAnalysisResponse,
    RiskEventRequest, RiskEventResponse
)
from a2a_adapter import (
    InvestmentA2AAdapter, RiskA2AAdapter, PortfolioA2AAdapter
)

# 기존 모듈들 import
from agent_graph import investment_agent
from portfolio_manager import portfolio_manager
from portfolio_analyzer import portfolio_analyzer
from memory_manager import memory_manager
from investment_profile import InvestmentProfile

logger = logging.getLogger(__name__)

class A2AIntegrationManager:
    """A2A 연동 관리자"""
    
    def __init__(self):
        self.adapters = {}
        self.initialized = False
        self.registry_endpoint = "ws://localhost:8765/registry"
        
    async def initialize(self):
        """A2A 연동 초기화"""
        if self.initialized:
            return
            
        try:
            # 1. 투자 분석 에이전트 어댑터 초기화
            investment_adapter = InvestmentA2AAdapter("websocket")
            investment_capabilities = AgentCapability(
                role=AgentRole.INVESTMENT_ANALYST,
                capabilities=[
                    "stock_analysis", "technical_analysis", "fundamental_analysis",
                    "investment_recommendations", "portfolio_optimization",
                    "risk_assessment", "market_research"
                ],
                supported_tickers=["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX"],
                supported_timeframes=["1d", "1w", "1m", "3m", "6m", "1y", "5y"],
                max_concurrent_requests=10,
                response_time_avg=2.5,
                version="1.0.0"
            )
            investment_adapter.register_capabilities(investment_capabilities)
            self.adapters["investment"] = investment_adapter
            
            # 2. 리스크 분석 에이전트 어댑터 초기화
            risk_adapter = RiskA2AAdapter("websocket")
            risk_capabilities = AgentCapability(
                role=AgentRole.RISK_ASSESSOR,
                capabilities=[
                    "risk_event_detection", "risk_scoring", "risk_factor_analysis",
                    "news_sentiment_analysis", "market_volatility_assessment",
                    "portfolio_risk_analysis", "stress_testing"
                ],
                supported_tickers=["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX"],
                supported_timeframes=["1h", "1d", "1w", "1m"],
                max_concurrent_requests=15,
                response_time_avg=1.8,
                version="1.0.0"
            )
            risk_adapter.register_capabilities(risk_capabilities)
            self.adapters["risk"] = risk_adapter
            
            # 3. 포트폴리오 관리 에이전트 어댑터 초기화
            portfolio_adapter = PortfolioA2AAdapter("websocket")
            portfolio_capabilities = AgentCapability(
                role=AgentRole.PORTFOLIO_MANAGER,
                capabilities=[
                    "portfolio_analysis", "position_management", "rebalancing",
                    "performance_tracking", "diversification_analysis",
                    "sector_allocation", "risk_metrics_calculation"
                ],
                supported_tickers=["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX"],
                supported_timeframes=["1d", "1w", "1m", "3m", "6m", "1y"],
                max_concurrent_requests=8,
                response_time_avg=3.2,
                version="1.0.0"
            )
            portfolio_adapter.register_capabilities(portfolio_capabilities)
            self.adapters["portfolio"] = portfolio_adapter
            
            # 4. 각 어댑터 서버 시작
            ports = {"investment": 8766, "risk": 8767, "portfolio": 8768}
            
            for adapter_name, adapter in self.adapters.items():
                port = ports[adapter_name]
                await adapter.start_server(port)
                logger.info(f"{adapter_name} adapter started on port {port}")
            
            self.initialized = True
            logger.info("A2A integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize A2A integration: {e}")
            raise
    
    async def start_collaborative_analysis(self, ticker: str, user_id: str, 
                                         analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """다중 에이전트 협업 분석 시작"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # 1. 각 에이전트에게 분석 요청
            tasks = []
            
            # 투자 분석 요청
            investment_task = self.adapters["investment"].request_stock_analysis(
                "investment_agent_001", ticker, analysis_type, "1m"
            )
            tasks.append(("investment", investment_task))
            
            # 리스크 분석 요청
            risk_task = self.adapters["risk"].request_risk_analysis(
                "risk_agent_001", ticker, ["news", "financial_reports", "market_data"]
            )
            tasks.append(("risk", risk_task))
            
            # 사용자 포트폴리오 분석 요청
            user_profile = memory_manager.get_user_profile(user_id)
            if user_profile:
                portfolio_data = self._get_user_portfolio_data(user_id)
                portfolio_task = self.adapters["portfolio"].request_portfolio_analysis(
                    "portfolio_agent_001", user_id, portfolio_data, ["risk_assessment", "optimization"]
                )
                tasks.append(("portfolio", portfolio_task))
            
            # 모든 분석 결과 수집
            results = {}
            for agent_name, task in tasks:
                try:
                    result = await asyncio.wait_for(task, timeout=30)
                    if result:
                        results[agent_name] = result
                        logger.info(f"{agent_name} analysis completed")
                    else:
                        logger.warning(f"{agent_name} analysis failed or timed out")
                except asyncio.TimeoutError:
                    logger.warning(f"{agent_name} analysis timed out")
                except Exception as e:
                    logger.error(f"{agent_name} analysis error: {e}")
            
            # 2. 결과 통합 및 종합 분석
            integrated_analysis = self._integrate_analysis_results(ticker, results)
            
            return integrated_analysis
            
        except Exception as e:
            logger.error(f"Collaborative analysis failed: {e}")
            return {"error": str(e)}
    
    def _get_user_portfolio_data(self, user_id: str) -> Dict[str, Any]:
        """사용자 포트폴리오 데이터 추출"""
        try:
            positions = portfolio_manager.get_positions_list(user_id)
            summary = portfolio_manager.get_portfolio_summary(user_id)
            
            return {
                "positions": positions,
                "summary": summary,
                "user_id": user_id
            }
        except Exception as e:
            logger.error(f"Failed to get portfolio data: {e}")
            return {"positions": [], "summary": {}, "user_id": user_id}
    
    def _integrate_analysis_results(self, ticker: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """분석 결과 통합"""
        integrated = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "collaborative",
            "agents_used": list(results.keys()),
            "integrated_score": 0.0,
            "recommendations": [],
            "risk_assessment": {},
            "investment_analysis": {},
            "portfolio_impact": {},
            "confidence_score": 0.0
        }
        
        # 투자 분석 결과 통합
        if "investment" in results:
            investment_data = results["investment"]
            integrated["investment_analysis"] = investment_data
            if "overall_score" in investment_data:
                integrated["integrated_score"] += investment_data["overall_score"] * 0.4
        
        # 리스크 분석 결과 통합
        if "risk" in results:
            risk_data = results["risk"]
            integrated["risk_assessment"] = risk_data
            if "overall_risk_score" in risk_data:
                # 리스크 점수를 반대로 변환 (높은 리스크 = 낮은 점수)
                risk_penalty = (100 - risk_data["overall_risk_score"]) * 0.3
                integrated["integrated_score"] -= risk_penalty
        
        # 포트폴리오 분석 결과 통합
        if "portfolio" in results:
            portfolio_data = results["portfolio"]
            integrated["portfolio_impact"] = portfolio_data
            if "overall_score" in portfolio_data:
                integrated["integrated_score"] += portfolio_data["overall_score"] * 0.3
        
        # 종합 추천 생성
        integrated["recommendations"] = self._generate_integrated_recommendations(
            integrated["integrated_score"], 
            integrated["risk_assessment"],
            integrated["investment_analysis"]
        )
        
        # 신뢰도 계산
        integrated["confidence_score"] = self._calculate_confidence_score(results)
        
        return integrated
    
    def _generate_integrated_recommendations(self, score: float, risk_data: Dict, 
                                           investment_data: Dict) -> List[Dict[str, Any]]:
        """통합 추천 생성"""
        recommendations = []
        
        # 기본 추천
        if score >= 70:
            action = "STRONG_BUY"
            confidence = "HIGH"
        elif score >= 50:
            action = "BUY"
            confidence = "MEDIUM"
        elif score >= 30:
            action = "HOLD"
            confidence = "MEDIUM"
        else:
            action = "SELL"
            confidence = "HIGH"
        
        recommendations.append({
            "action": action,
            "confidence": confidence,
            "score": score,
            "reasoning": f"통합 분석 점수 {score:.1f}점 기반"
        })
        
        # 리스크 기반 추천
        if risk_data and "risk_level" in risk_data:
            risk_level = risk_data["risk_level"]
            if risk_level in ["high", "critical"]:
                recommendations.append({
                    "action": "REDUCE_POSITION",
                    "confidence": "HIGH",
                    "reasoning": f"높은 리스크 레벨 감지: {risk_level}"
                })
        
        # 투자 분석 기반 추천
        if investment_data and "recommendations" in investment_data:
            for rec in investment_data["recommendations"]:
                if isinstance(rec, dict) and "recommendation" in rec:
                    recommendations.append({
                        "action": rec["recommendation"],
                        "confidence": rec.get("confidence", "MEDIUM"),
                        "reasoning": "투자 분석 에이전트 추천"
                    })
        
        return recommendations
    
    def _calculate_confidence_score(self, results: Dict[str, Any]) -> float:
        """신뢰도 점수 계산"""
        if not results:
            return 0.0
        
        total_confidence = 0.0
        count = 0
        
        for agent_name, result in results.items():
            if isinstance(result, dict):
                # 각 에이전트의 신뢰도 추출
                if "confidence_score" in result:
                    total_confidence += result["confidence_score"]
                    count += 1
                elif "confidence" in result:
                    # 문자열 신뢰도를 숫자로 변환
                    conf_str = str(result["confidence"]).lower()
                    if "high" in conf_str:
                        total_confidence += 0.8
                    elif "medium" in conf_str:
                        total_confidence += 0.6
                    elif "low" in conf_str:
                        total_confidence += 0.4
                    count += 1
        
        if count > 0:
            return total_confidence / count
        else:
            return 0.5  # 기본 신뢰도
    
    async def register_with_external_agents(self, external_agents: List[Dict[str, Any]]):
        """외부 에이전트들과 등록"""
        if not self.initialized:
            await self.initialize()
        
        for agent_info in external_agents:
            agent_id = agent_info.get("agent_id")
            endpoint = agent_info.get("endpoint")
            role = agent_info.get("role")
            
            if agent_id and endpoint:
                try:
                    # 해당 에이전트에 연결 시도
                    for adapter in self.adapters.values():
                        if await adapter.transport.connect(endpoint):
                            logger.info(f"Connected to external agent: {agent_id}")
                            break
                except Exception as e:
                    logger.error(f"Failed to connect to external agent {agent_id}: {e}")
    
    async def handle_external_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """외부 에이전트 요청 처리"""
        try:
            request_type = request.get("type")
            ticker = request.get("ticker")
            user_id = request.get("user_id", "external_user")
            
            if request_type == "stock_analysis" and ticker:
                # 외부 에이전트의 주식 분석 요청 처리
                result = await self.start_collaborative_analysis(ticker, user_id)
                return result
            elif request_type == "portfolio_analysis" and user_id:
                # 외부 에이전트의 포트폴리오 분석 요청 처리
                portfolio_data = self._get_user_portfolio_data(user_id)
                analysis = portfolio_analyzer.analyze_portfolio(
                    user_id, memory_manager.get_user_profile(user_id)
                )
                return {
                    "user_id": user_id,
                    "analysis": analysis,
                    "portfolio_data": portfolio_data
                }
            else:
                return {"error": "Invalid request type or missing parameters"}
                
        except Exception as e:
            logger.error(f"Failed to handle external request: {e}")
            return {"error": str(e)}
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """에이전트 상태 조회"""
        status = {
            "initialized": self.initialized,
            "adapters": {},
            "registry_endpoint": self.registry_endpoint,
            "timestamp": datetime.now().isoformat()
        }
        
        for adapter_name, adapter in self.adapters.items():
            status["adapters"][adapter_name] = {
                "agent_id": adapter.agent_id,
                "role": adapter.agent_role.value,
                "capabilities": adapter.capabilities.role.value if adapter.capabilities else None,
                "pending_requests": len(adapter.pending_requests),
                "registered_agents": len(adapter.registered_agents)
            }
        
        return status
    
    async def shutdown(self):
        """A2A 연동 종료"""
        logger.info("Shutting down A2A integration...")
        
        for adapter_name, adapter in self.adapters.items():
            try:
                # 대기 중인 요청 정리
                await adapter.cleanup_expired_requests()
                logger.info(f"{adapter_name} adapter cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up {adapter_name} adapter: {e}")
        
        self.initialized = False
        logger.info("A2A integration shutdown complete")

# 전역 A2A 통합 관리자
a2a_manager = A2AIntegrationManager()

async def main():
    """A2A 연동 테스트 메인 함수"""
    print("🚀 A2A Integration Manager 시작")
    
    # A2A 연동 초기화
    await a2a_manager.initialize()
    
    # 상태 조회
    status = await a2a_manager.get_agent_status()
    print(f"📊 A2A 상태: {status}")
    
    # 협업 분석 테스트
    print("\n🔍 AAPL 협업 분석 시작...")
    result = await a2a_manager.start_collaborative_analysis("AAPL", "test_user")
    print(f"📈 분석 결과: {result}")
    
    # 종료
    await a2a_manager.shutdown()
    print("✅ A2A 연동 완료")

if __name__ == "__main__":
    asyncio.run(main())
