#!/usr/bin/env python3
"""
A2A 연동 간단 데모
의존성 없이 실행 가능한 A2A 연동 시연
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# 간단한 A2A 프로토콜 구현 (의존성 최소화)
class SimpleA2AMessage:
    def __init__(self, sender_id: str, receiver_id: str, message_type: str, payload: Dict[str, Any]):
        self.message_id = f"msg_{datetime.now().timestamp()}"
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message_type = message_type
        self.payload = payload
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp
        }

class SimpleA2AAgent:
    """간단한 A2A 에이전트"""
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.received_messages = []
        self.sent_messages = []
    
    async def send_message(self, receiver_id: str, message_type: str, payload: Dict[str, Any]) -> SimpleA2AMessage:
        """메시지 전송"""
        message = SimpleA2AMessage(self.agent_id, receiver_id, message_type, payload)
        self.sent_messages.append(message)
        print(f"📤 {self.agent_id} -> {receiver_id}: {message_type}")
        return message
    
    async def receive_message(self, message: SimpleA2AMessage):
        """메시지 수신"""
        self.received_messages.append(message)
        print(f"📥 {message.sender_id} -> {self.agent_id}: {message.message_type}")
        
        # 메시지 타입별 처리
        if message.message_type == "analysis_request":
            await self.handle_analysis_request(message)
        elif message.message_type == "analysis_response":
            await self.handle_analysis_response(message)
    
    async def handle_analysis_request(self, message: SimpleA2AMessage):
        """분석 요청 처리"""
        ticker = message.payload.get("ticker", "UNKNOWN")
        
        # 시뮬레이션된 분석 결과 생성
        if self.agent_type == "investment":
            analysis_result = {
                "ticker": ticker,
                "current_price": 150.0 + hash(ticker) % 100,
                "recommendation": "BUY" if hash(ticker) % 2 == 0 else "HOLD",
                "confidence": 0.8,
                "analysis_type": "investment"
            }
        elif self.agent_type == "risk":
            analysis_result = {
                "ticker": ticker,
                "risk_score": 20 + hash(ticker) % 50,
                "risk_level": "low" if hash(ticker) % 3 == 0 else "medium",
                "risk_factors": ["market_volatility", "sector_risk"],
                "analysis_type": "risk"
            }
        elif self.agent_type == "portfolio":
            analysis_result = {
                "ticker": ticker,
                "portfolio_weight": 5.0 + hash(ticker) % 10,
                "diversification_score": 0.7,
                "rebalancing_needed": hash(ticker) % 2 == 0,
                "analysis_type": "portfolio"
            }
        else:
            analysis_result = {"error": "Unknown agent type"}
        
        # 응답 전송
        response = await self.send_message(
            message.sender_id, 
            "analysis_response", 
            analysis_result
        )
    
    async def handle_analysis_response(self, message: SimpleA2AMessage):
        """분석 응답 처리"""
        result = message.payload
        print(f"  📊 분석 결과: {result}")

class SimpleA2ACoordinator:
    """간단한 A2A 조정자"""
    
    def __init__(self):
        self.agents = {}
        self.coordination_results = {}
    
    def register_agent(self, agent: SimpleA2AAgent):
        """에이전트 등록"""
        self.agents[agent.agent_id] = agent
        print(f"🤖 {agent.agent_id} ({agent.agent_type}) 에이전트 등록됨")
    
    async def coordinate_analysis(self, ticker: str) -> Dict[str, Any]:
        """협업 분석 조정"""
        print(f"\n🔍 {ticker} 협업 분석 시작")
        
        # 모든 에이전트에게 분석 요청
        requests = []
        for agent_id, agent in self.agents.items():
            request = await agent.send_message(
                "coordinator", 
                "analysis_request", 
                {"ticker": ticker, "request_id": f"req_{ticker}_{agent_id}"}
            )
            requests.append((agent_id, request))
        
        # 응답 수집 (실제로는 비동기적으로 처리)
        await asyncio.sleep(0.1)  # 시뮬레이션된 처리 시간
        
        # 각 에이전트의 응답 시뮬레이션
        results = {}
        for agent_id, agent in self.agents.items():
            # 시뮬레이션된 분석 결과 생성
            if agent.agent_type == "investment":
                result = {
                    "ticker": ticker,
                    "current_price": 150.0 + hash(ticker) % 100,
                    "recommendation": "BUY" if hash(ticker) % 2 == 0 else "HOLD",
                    "confidence": 0.8,
                    "analysis_type": "investment"
                }
            elif agent.agent_type == "risk":
                result = {
                    "ticker": ticker,
                    "risk_score": 20 + hash(ticker) % 50,
                    "risk_level": "low" if hash(ticker) % 3 == 0 else "medium",
                    "risk_factors": ["market_volatility", "sector_risk"],
                    "analysis_type": "risk"
                }
            elif agent.agent_type == "portfolio":
                result = {
                    "ticker": ticker,
                    "portfolio_weight": 5.0 + hash(ticker) % 10,
                    "diversification_score": 0.7,
                    "rebalancing_needed": hash(ticker) % 2 == 0,
                    "analysis_type": "portfolio"
                }
            
            results[agent_id] = result
            
            # 에이전트에게 응답 전달
            response_msg = SimpleA2AMessage(
                "coordinator", agent_id, "analysis_response", result
            )
            await agent.receive_message(response_msg)
        
        # 결과 통합
        integrated_result = self.integrate_results(ticker, results)
        
        print(f"✅ {ticker} 협업 분석 완료")
        return integrated_result
    
    def integrate_results(self, ticker: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """분석 결과 통합"""
        print(f"\n🔗 {ticker} 분석 결과 통합 중...")
        
        integrated = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "agents_participated": list(results.keys()),
            "individual_results": results,
            "integrated_score": 0.0,
            "final_recommendation": "HOLD",
            "confidence": 0.0,
            "risk_assessment": {},
            "portfolio_impact": {}
        }
        
        # 투자 분석 결과 처리
        for agent_id, result in results.items():
            if result.get("analysis_type") == "investment":
                integrated["current_price"] = result.get("current_price", 0)
                integrated["final_recommendation"] = result.get("recommendation", "HOLD")
                integrated["confidence"] = result.get("confidence", 0.5)
                integrated["integrated_score"] += 60  # 투자 분석 가중치
                
            elif result.get("analysis_type") == "risk":
                integrated["risk_assessment"] = {
                    "risk_score": result.get("risk_score", 50),
                    "risk_level": result.get("risk_level", "medium"),
                    "risk_factors": result.get("risk_factors", [])
                }
                # 리스크 점수 반영 (높은 리스크 = 낮은 점수)
                risk_penalty = max(0, result.get("risk_score", 50) - 30)
                integrated["integrated_score"] -= risk_penalty * 0.5
                
            elif result.get("analysis_type") == "portfolio":
                integrated["portfolio_impact"] = {
                    "current_weight": result.get("portfolio_weight", 0),
                    "diversification_score": result.get("diversification_score", 0),
                    "rebalancing_needed": result.get("rebalancing_needed", False)
                }
                # 포트폴리오 최적화 점수 반영
                portfolio_score = result.get("diversification_score", 0.5) * 20
                integrated["integrated_score"] += portfolio_score
        
        # 최종 점수 정규화 (0-100)
        integrated["integrated_score"] = max(0, min(100, integrated["integrated_score"]))
        
        # 최종 추천 조정
        if integrated["integrated_score"] >= 70:
            integrated["final_recommendation"] = "STRONG_BUY"
        elif integrated["integrated_score"] >= 50:
            integrated["final_recommendation"] = "BUY"
        elif integrated["integrated_score"] >= 30:
            integrated["final_recommendation"] = "HOLD"
        else:
            integrated["final_recommendation"] = "SELL"
        
        print(f"📊 통합 결과:")
        print(f"  종목: {integrated['ticker']}")
        print(f"  통합 점수: {integrated['integrated_score']:.1f}/100")
        print(f"  최종 추천: {integrated['final_recommendation']}")
        print(f"  신뢰도: {integrated['confidence']:.1f}")
        print(f"  참여 에이전트: {', '.join(integrated['agents_participated'])}")
        
        return integrated

async def run_a2a_demo():
    """A2A 연동 데모 실행"""
    print("🎭 A2A 연동 간단 데모")
    print("=" * 40)
    
    # 조정자 생성
    coordinator = SimpleA2ACoordinator()
    
    # 에이전트들 생성 및 등록
    agents = [
        SimpleA2AAgent("investment_001", "investment"),
        SimpleA2AAgent("risk_001", "risk"),
        SimpleA2AAgent("portfolio_001", "portfolio")
    ]
    
    for agent in agents:
        coordinator.register_agent(agent)
    
    print(f"\n🤖 총 {len(agents)}개 에이전트 등록 완료")
    
    # AAPL 협업 분석
    print(f"\n" + "="*40)
    aapl_result = await coordinator.coordinate_analysis("AAPL")
    
    # TSLA 협업 분석
    print(f"\n" + "="*40)
    tsla_result = await coordinator.coordinate_analysis("TSLA")
    
    # MSFT 협업 분석
    print(f"\n" + "="*40)
    msft_result = await coordinator.coordinate_analysis("MSFT")
    
    # 결과 요약
    print(f"\n📊 분석 결과 요약")
    print("=" * 40)
    
    results = [("AAPL", aapl_result), ("TSLA", tsla_result), ("MSFT", msft_result)]
    
    for ticker, result in results:
        print(f"  {ticker}: {result['final_recommendation']} (점수: {result['integrated_score']:.1f})")
    
    # 최고 추천 종목
    best_stock = max(results, key=lambda x: x[1]['integrated_score'])
    print(f"\n🏆 최고 추천: {best_stock[0]} (점수: {best_stock[1]['integrated_score']:.1f})")
    
    print(f"\n✅ A2A 연동 데모 완료!")
    print(f"💡 실제 구현에서는 WebSocket, HTTP API, 메시지 큐 등을 사용하여")
    print(f"   더 정교한 A2A 통신을 구현할 수 있습니다.")

if __name__ == "__main__":
    asyncio.run(run_a2a_demo())
