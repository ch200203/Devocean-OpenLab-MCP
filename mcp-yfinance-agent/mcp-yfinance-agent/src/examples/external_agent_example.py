#!/usr/bin/env python3
"""
외부 AI 에이전트가 우리 시스템과 연동하는 완전한 예제
다른 AI 에이전트 개발자들이 참고할 수 있는 실제 구현 코드
"""

import asyncio
import websockets
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExternalAIAgent:
    """외부 AI 에이전트 - 우리 시스템과 A2A 연동"""
    
    def __init__(self, agent_id: str, agent_name: str = "External AI Agent"):
        self.agent_id = agent_id
        self.agent_name = agent_name
        
        # 우리 시스템의 엔드포인트들
        self.endpoints = {
            "investment": "ws://localhost:8766",
            "risk": "ws://localhost:8767",
            "portfolio": "ws://localhost:8768",
            "http_api": "http://localhost:8000/a2a"
        }
        
        # 연결 상태
        self.connections = {}
        self.message_history = []
        
    async def connect_to_services(self) -> bool:
        """모든 서비스에 연결"""
        print(f"🔗 {self.agent_name} 서비스 연결 중...")
        
        success_count = 0
        
        for service_name, endpoint in self.endpoints.items():
            if service_name == "http_api":
                # HTTP API는 연결 테스트만
                if await self._test_http_connection(endpoint):
                    success_count += 1
                    print(f"✅ HTTP API 연결 성공")
            else:
                # WebSocket 연결 테스트
                if await self._test_websocket_connection(endpoint):
                    success_count += 1
                    print(f"✅ {service_name} WebSocket 연결 성공")
        
        print(f"📊 연결 결과: {success_count}/{len(self.endpoints)} 서비스 연결 성공")
        return success_count > 0
    
    async def _test_websocket_connection(self, endpoint: str) -> bool:
        """WebSocket 연결 테스트"""
        try:
            async with websockets.connect(endpoint, timeout=5) as websocket:
                return True
        except Exception as e:
            logger.warning(f"WebSocket 연결 실패 {endpoint}: {e}")
            return False
    
    async def _test_http_connection(self, endpoint: str) -> bool:
        """HTTP API 연결 테스트"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{endpoint}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"HTTP API 연결 실패 {endpoint}: {e}")
            return False
    
    async def analyze_stock_comprehensive(self, ticker: str, user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """종합적인 주식 분석 (우리 시스템의 모든 에이전트 활용)"""
        print(f"\n🔍 {ticker} 종합 분석 시작...")
        
        # 기본 사용자 프로필
        if not user_profile:
            user_profile = {
                "risk_tolerance": "moderate",
                "investment_horizon": "short_term",
                "trading_style": "swing_trading"
            }
        
        # 병렬로 여러 분석 실행
        tasks = [
            self._request_investment_analysis(ticker, user_profile),
            self._request_risk_analysis(ticker),
            self._request_portfolio_impact(ticker, user_profile)
        ]
        
        # 모든 분석 완료 대기
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        investment_result, risk_result, portfolio_result = results
        
        # 결과 통합
        integrated_analysis = self._integrate_comprehensive_analysis(
            ticker, investment_result, risk_result, portfolio_result
        )
        
        return integrated_analysis
    
    async def _request_investment_analysis(self, ticker: str, user_profile: Dict) -> Dict[str, Any]:
        """투자 분석 요청"""
        message = {
            "message_id": f"msg_{int(time.time())}_inv_{ticker}",
            "sender_id": self.agent_id,
            "receiver_id": "investment_agent_001",
            "message_type": "request",
            "priority": "high",
            "timestamp": datetime.now().isoformat(),
            "payload": {
                "ticker": ticker,
                "analysis_type": "comprehensive",
                "timeframe": "1m",
                "user_profile": user_profile
            }
        }
        
        try:
            async with websockets.connect(self.endpoints["investment"], timeout=10) as websocket:
                await websocket.send(json.dumps(message))
                
                # 응답 대기 (타임아웃 설정)
                response = await asyncio.wait_for(websocket.recv(), timeout=15)
                result = json.loads(response)
                
                self.message_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "investment_request",
                    "ticker": ticker,
                    "status": "success" if result.get("message_type") == "response" else "failed"
                })
                
                if result.get("message_type") == "response":
                    print(f"  ✅ 투자 분석 완료: {ticker}")
                    return result["payload"]
                else:
                    print(f"  ❌ 투자 분석 실패: {result.get('payload', {}).get('error_message', 'Unknown error')}")
                    return {}
                    
        except asyncio.TimeoutError:
            print(f"  ⏰ 투자 분석 시간 초과: {ticker}")
            return {}
        except Exception as e:
            print(f"  ❌ 투자 분석 오류: {e}")
            return {}
    
    async def _request_risk_analysis(self, ticker: str) -> Dict[str, Any]:
        """리스크 분석 요청"""
        message = {
            "message_id": f"msg_{int(time.time())}_risk_{ticker}",
            "sender_id": self.agent_id,
            "receiver_id": "risk_agent_001",
            "message_type": "request",
            "priority": "high",
            "timestamp": datetime.now().isoformat(),
            "payload": {
                "ticker": ticker,
                "event_sources": ["news", "financial_reports", "market_data"],
                "time_horizon": "1d",
                "severity_threshold": "medium"
            }
        }
        
        try:
            async with websockets.connect(self.endpoints["risk"], timeout=10) as websocket:
                await websocket.send(json.dumps(message))
                
                response = await asyncio.wait_for(websocket.recv(), timeout=15)
                result = json.loads(response)
                
                self.message_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "risk_request",
                    "ticker": ticker,
                    "status": "success" if result.get("message_type") == "response" else "failed"
                })
                
                if result.get("message_type") == "response":
                    print(f"  ✅ 리스크 분석 완료: {ticker}")
                    return result["payload"]
                else:
                    print(f"  ❌ 리스크 분석 실패: {result.get('payload', {}).get('error_message', 'Unknown error')}")
                    return {}
                    
        except asyncio.TimeoutError:
            print(f"  ⏰ 리스크 분석 시간 초과: {ticker}")
            return {}
        except Exception as e:
            print(f"  ❌ 리스크 분석 오류: {e}")
            return {}
    
    async def _request_portfolio_impact(self, ticker: str, user_profile: Dict) -> Dict[str, Any]:
        """포트폴리오 영향 분석 요청"""
        # 시뮬레이션된 포트폴리오 데이터
        portfolio_data = {
            "positions": [
                {"ticker": "AAPL", "quantity": 100, "average_price": 150.0},
                {"ticker": "GOOGL", "quantity": 50, "average_price": 2500.0},
                {"ticker": "MSFT", "quantity": 75, "average_price": 300.0}
            ],
            "cash": 10000.0,
            "total_value": 50000.0
        }
        
        message = {
            "message_id": f"msg_{int(time.time())}_port_{ticker}",
            "sender_id": self.agent_id,
            "receiver_id": "portfolio_agent_001",
            "message_type": "request",
            "priority": "high",
            "timestamp": datetime.now().isoformat(),
            "payload": {
                "user_id": f"external_user_{self.agent_id}",
                "portfolio_data": portfolio_data,
                "analysis_goals": ["risk_assessment", "diversification", "rebalancing"]
            }
        }
        
        try:
            async with websockets.connect(self.endpoints["portfolio"], timeout=10) as websocket:
                await websocket.send(json.dumps(message))
                
                response = await asyncio.wait_for(websocket.recv(), timeout=15)
                result = json.loads(response)
                
                self.message_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "portfolio_request",
                    "ticker": ticker,
                    "status": "success" if result.get("message_type") == "response" else "failed"
                })
                
                if result.get("message_type") == "response":
                    print(f"  ✅ 포트폴리오 분석 완료: {ticker}")
                    return result["payload"]
                else:
                    print(f"  ❌ 포트폴리오 분석 실패: {result.get('payload', {}).get('error_message', 'Unknown error')}")
                    return {}
                    
        except asyncio.TimeoutError:
            print(f"  ⏰ 포트폴리오 분석 시간 초과: {ticker}")
            return {}
        except Exception as e:
            print(f"  ❌ 포트폴리오 분석 오류: {e}")
            return {}
    
    def _integrate_comprehensive_analysis(self, ticker: str, investment_result: Dict, 
                                        risk_result: Dict, portfolio_result: Dict) -> Dict[str, Any]:
        """종합 분석 결과 통합"""
        print(f"  🔗 {ticker} 분석 결과 통합 중...")
        
        integrated = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "external_agent_id": self.agent_id,
            "external_agent_name": self.agent_name,
            "analysis_components": {
                "investment_analysis": investment_result,
                "risk_analysis": risk_result,
                "portfolio_analysis": portfolio_result
            },
            "final_score": 0.0,
            "final_recommendation": "HOLD",
            "confidence_score": 0.0,
            "risk_level": "medium",
            "key_insights": [],
            "recommendations": []
        }
        
        # 투자 분석 결과 처리
        if investment_result:
            investment_score = investment_result.get("overall_score", 50)
            integrated["final_score"] += investment_score * 0.5  # 50% 가중치
            integrated["confidence_score"] = investment_result.get("confidence", 0.5)
            
            # 추천 처리
            recommendations = investment_result.get("recommendations", [])
            if recommendations:
                primary_rec = recommendations[0]
                integrated["final_recommendation"] = primary_rec.get("action", "HOLD")
                integrated["recommendations"].append({
                    "type": "investment",
                    "action": primary_rec.get("action", "HOLD"),
                    "reasoning": primary_rec.get("reasoning", "투자 분석 기반"),
                    "confidence": primary_rec.get("confidence", 0.5)
                })
            
            # 주요 인사이트
            if investment_score > 70:
                integrated["key_insights"].append("강한 투자 매력도")
            elif investment_score < 30:
                integrated["key_insights"].append("낮은 투자 매력도")
        
        # 리스크 분석 결과 처리
        if risk_result:
            risk_score = risk_result.get("overall_risk_score", 50)
            risk_level = risk_result.get("risk_level", "medium")
            integrated["risk_level"] = risk_level
            
            # 리스크 점수 반영 (높은 리스크 = 낮은 점수)
            risk_penalty = max(0, risk_score - 30) * 0.4
            integrated["final_score"] -= risk_penalty
            
            # 리스크 기반 추천 조정
            if risk_score > 70:
                if integrated["final_recommendation"] in ["BUY", "STRONG_BUY"]:
                    integrated["final_recommendation"] = "HOLD"
                    integrated["recommendations"].append({
                        "type": "risk",
                        "action": "REDUCE_EXPOSURE",
                        "reasoning": "높은 리스크 수준",
                        "confidence": 0.8
                    })
            
            # 리스크 인사이트
            risk_factors = risk_result.get("risk_factors", [])
            if risk_factors:
                integrated["key_insights"].append(f"리스크 팩터: {', '.join(risk_factors[:2])}")
        
        # 포트폴리오 분석 결과 처리
        if portfolio_result:
            portfolio_score = portfolio_result.get("overall_score", 50)
            integrated["final_score"] += portfolio_score * 0.2  # 20% 가중치
            
            # 포트폴리오 최적화 추천
            recommendations = portfolio_result.get("recommendations", [])
            if recommendations:
                for rec in recommendations[:2]:  # 최대 2개 추천
                    integrated["recommendations"].append({
                        "type": "portfolio",
                        "action": rec.get("action", "HOLD"),
                        "reasoning": rec.get("reasoning", "포트폴리오 최적화"),
                        "confidence": rec.get("confidence", 0.6)
                    })
        
        # 최종 점수 정규화 (0-100)
        integrated["final_score"] = max(0, min(100, integrated["final_score"]))
        
        # 최종 추천 조정
        if integrated["final_score"] >= 80:
            integrated["final_recommendation"] = "STRONG_BUY"
        elif integrated["final_score"] >= 65:
            integrated["final_recommendation"] = "BUY"
        elif integrated["final_score"] >= 35:
            integrated["final_recommendation"] = "HOLD"
        elif integrated["final_score"] >= 20:
            integrated["final_recommendation"] = "SELL"
        else:
            integrated["final_recommendation"] = "STRONG_SELL"
        
        # 종합 인사이트 추가
        if integrated["final_score"] > 70:
            integrated["key_insights"].append("전반적으로 긍정적인 분석 결과")
        elif integrated["final_score"] < 30:
            integrated["key_insights"].append("전반적으로 부정적인 분석 결과")
        
        print(f"  📊 통합 완료: {integrated['final_recommendation']} (점수: {integrated['final_score']:.1f})")
        
        return integrated
    
    async def batch_analysis(self, tickers: List[str], user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """배치 분석 (여러 종목 동시 분석)"""
        print(f"\n📊 {len(tickers)}개 종목 배치 분석 시작...")
        
        start_time = time.time()
        
        # 병렬로 모든 분석 실행
        tasks = []
        for ticker in tickers:
            task = self.analyze_stock_comprehensive(ticker, user_profile)
            tasks.append((ticker, task))
        
        # 모든 분석 완료 대기
        results = {}
        successful_count = 0
        
        for ticker, task in tasks:
            try:
                result = await task
                if "error" not in result:
                    results[ticker] = result
                    successful_count += 1
                    print(f"✅ {ticker}: {result['final_recommendation']} (점수: {result['final_score']:.1f})")
                else:
                    results[ticker] = {"error": "분석 실패"}
                    print(f"❌ {ticker}: 분석 실패")
            except Exception as e:
                results[ticker] = {"error": str(e)}
                print(f"❌ {ticker}: 오류 - {e}")
        
        end_time = time.time()
        
        # 결과 요약
        if successful_count > 0:
            successful_results = [r for r in results.values() if "error" not in r]
            best_stock = max(successful_results, key=lambda x: x["final_score"])
            worst_stock = min(successful_results, key=lambda x: x["final_score"])
            
            summary = {
                "total_analyzed": len(tickers),
                "successful": successful_count,
                "failed": len(tickers) - successful_count,
                "success_rate": successful_count / len(tickers),
                "analysis_time": end_time - start_time,
                "average_time_per_stock": (end_time - start_time) / len(tickers),
                "best_recommendation": {
                    "ticker": best_stock["ticker"],
                    "recommendation": best_stock["final_recommendation"],
                    "score": best_stock["final_score"]
                },
                "worst_recommendation": {
                    "ticker": worst_stock["ticker"],
                    "recommendation": worst_stock["final_recommendation"],
                    "score": worst_stock["final_score"]
                },
                "average_score": sum(r["final_score"] for r in successful_results) / len(successful_results),
                "detailed_results": results
            }
            
            print(f"\n📈 배치 분석 완료:")
            print(f"  성공률: {successful_count}/{len(tickers)} ({summary['success_rate']*100:.1f}%)")
            print(f"  분석 시간: {summary['analysis_time']:.2f}초")
            print(f"  최고 추천: {summary['best_recommendation']['ticker']} ({summary['best_recommendation']['recommendation']})")
            print(f"  평균 점수: {summary['average_score']:.1f}")
            
            return summary
        else:
            return {
                "error": "모든 분석이 실패했습니다",
                "total_analyzed": len(tickers),
                "successful": 0,
                "failed": len(tickers),
                "analysis_time": end_time - start_time
            }
    
    async def real_time_monitoring(self, tickers: List[str], duration_minutes: int = 5):
        """실시간 모니터링 (시뮬레이션)"""
        print(f"\n📡 {', '.join(tickers)} 실시간 모니터링 시작 ({duration_minutes}분)")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            for ticker in tickers:
                try:
                    # 간단한 실시간 분석 (실제로는 WebSocket 스트림 사용)
                    result = await self.analyze_stock_comprehensive(ticker)
                    print(f"📊 {ticker} 실시간: {result['final_recommendation']} (점수: {result['final_score']:.1f})")
                except Exception as e:
                    print(f"❌ {ticker} 실시간 모니터링 오류: {e}")
            
            # 30초 대기
            await asyncio.sleep(30)
        
        print(f"✅ 실시간 모니터링 완료")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """에이전트 상태 조회"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "endpoints": self.endpoints,
            "message_count": len(self.message_history),
            "last_activity": self.message_history[-1]["timestamp"] if self.message_history else None,
            "timestamp": datetime.now().isoformat()
        }
    
    def export_analysis_report(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """분석 결과 리포트 내보내기"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_report_{timestamp}.json"
        
        report = {
            "report_info": {
                "generated_by": self.agent_id,
                "agent_name": self.agent_name,
                "generated_at": datetime.now().isoformat(),
                "report_type": "comprehensive_stock_analysis"
            },
            "summary": results,
            "message_history": self.message_history
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 분석 리포트 내보내기 완료: {filename}")
        return filename

async def main():
    """메인 함수 - 외부 에이전트 실행 예제"""
    print("🤖 외부 AI 에이전트 A2A 연동 예제")
    print("=" * 60)
    
    # 외부 에이전트 생성
    external_agent = ExternalAIAgent("external_agent_001", "My Trading Bot")
    
    # 서비스 연결 확인
    if not await external_agent.connect_to_services():
        print("❌ 서비스 연결 실패. 서버가 실행 중인지 확인하세요.")
        print("💡 다음 명령어로 서버를 시작하세요:")
        print("   python3 a2a_integration.py")
        return
    
    try:
        # 1. 단일 종목 분석
        print(f"\n{'='*60}")
        print("🔍 단일 종목 분석 예제")
        print(f"{'='*60}")
        
        user_profile = {
            "risk_tolerance": "aggressive",
            "investment_horizon": "short_term",
            "trading_style": "swing_trading"
        }
        
        aapl_result = await external_agent.analyze_stock_comprehensive("AAPL", user_profile)
        
        print(f"\n📊 AAPL 분석 결과:")
        print(f"  최종 점수: {aapl_result['final_score']:.1f}/100")
        print(f"  최종 추천: {aapl_result['final_recommendation']}")
        print(f"  신뢰도: {aapl_result['confidence_score']:.2f}")
        print(f"  리스크 레벨: {aapl_result['risk_level']}")
        print(f"  주요 인사이트: {', '.join(aapl_result['key_insights'])}")
        
        # 2. 배치 분석
        print(f"\n{'='*60}")
        print("📊 배치 분석 예제")
        print(f"{'='*60}")
        
        tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "META", "NVDA"]
        batch_result = await external_agent.batch_analysis(tickers, user_profile)
        
        # 3. 결과 리포트 생성
        print(f"\n{'='*60}")
        print("📄 리포트 생성")
        print(f"{'='*60}")
        
        report_data = {
            "single_analysis": aapl_result,
            "batch_analysis": batch_result
        }
        
        report_file = external_agent.export_analysis_report(report_data)
        
        # 4. 에이전트 상태 조회
        print(f"\n{'='*60}")
        print("📋 에이전트 상태")
        print(f"{'='*60}")
        
        status = external_agent.get_agent_status()
        print(f"  에이전트 ID: {status['agent_id']}")
        print(f"  에이전트 이름: {status['agent_name']}")
        print(f"  처리된 메시지: {status['message_count']}")
        print(f"  마지막 활동: {status['last_activity']}")
        
        print(f"\n✅ 외부 에이전트 A2A 연동 예제 완료!")
        print(f"📄 상세 리포트: {report_file}")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n❌ 실행 중 오류 발생: {e}")
        logger.exception("상세 오류 정보:")

if __name__ == "__main__":
    asyncio.run(main())
