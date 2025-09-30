#!/usr/bin/env python3
"""
A2A 연동 테스트 스위트
다양한 시나리오를 통한 A2A 통신 및 협업 기능 검증
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List
from datetime import datetime

from a2a_protocol import (
    A2AMessage, MessageType, AgentRole, Priority,
    StockAnalysisRequest, PortfolioAnalysisRequest, RiskEventRequest,
    AgentCapability, A2AProtocol
)
from a2a_adapter import InvestmentA2AAdapter, RiskA2AAdapter, PortfolioA2AAdapter
from a2a_integration import A2AIntegrationManager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class A2ATestSuite:
    """A2A 연동 테스트 스위트"""
    
    def __init__(self):
        self.test_results = {}
        self.integration_manager = A2AIntegrationManager()
        
    async def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 A2A 연동 테스트 스위트 시작")
        print("=" * 60)
        
        tests = [
            ("프로토콜 테스트", self.test_protocol),
            ("어댑터 테스트", self.test_adapters),
            ("통합 관리자 테스트", self.test_integration_manager),
            ("협업 분석 테스트", self.test_collaborative_analysis),
            ("에러 처리 테스트", self.test_error_handling),
            ("성능 테스트", self.test_performance),
            ("외부 연동 테스트", self.test_external_integration)
        ]
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name} 실행 중...")
            try:
                start_time = time.time()
                result = await test_func()
                end_time = time.time()
                
                self.test_results[test_name] = {
                    "status": "PASSED" if result else "FAILED",
                    "duration": end_time - start_time,
                    "details": result if isinstance(result, dict) else {"success": result}
                }
                
                status_emoji = "✅" if result else "❌"
                print(f"{status_emoji} {test_name}: {self.test_results[test_name]['status']} ({end_time - start_time:.2f}s)")
                
            except Exception as e:
                self.test_results[test_name] = {
                    "status": "ERROR",
                    "duration": 0,
                    "details": {"error": str(e)}
                }
                print(f"❌ {test_name}: ERROR - {e}")
        
        # 테스트 결과 요약
        self.print_test_summary()
    
    async def test_protocol(self) -> bool:
        """A2A 프로토콜 테스트"""
        try:
            # 프로토콜 생성
            protocol = A2AProtocol("test_agent", AgentRole.INVESTMENT_ANALYST)
            
            # 능력 등록
            capabilities = AgentCapability(
                role=AgentRole.INVESTMENT_ANALYST,
                capabilities=["stock_analysis"],
                supported_tickers=["AAPL"],
                supported_timeframes=["1d"],
                max_concurrent_requests=1,
                response_time_avg=1.0,
                version="1.0.0"
            )
            protocol.register_capabilities(capabilities)
            
            # 메시지 생성 테스트
            message = protocol.create_message(
                "receiver", MessageType.REQUEST, {"test": "data"}
            )
            
            # 직렬화/역직렬화 테스트
            serialized = protocol.serialize_message(message)
            deserialized = protocol.deserialize_message(serialized)
            
            # 검증
            assert message.message_id == deserialized.message_id
            assert message.sender_id == deserialized.sender_id
            assert message.receiver_id == deserialized.receiver_id
            assert message.message_type == deserialized.message_type
            
            # 주식 분석 요청 테스트
            stock_request = protocol.create_stock_analysis_request(
                "analyst", "AAPL", "technical", "1d"
            )
            assert stock_request.payload["ticker"] == "AAPL"
            assert stock_request.payload["analysis_type"] == "technical"
            
            return True
            
        except Exception as e:
            logger.error(f"Protocol test failed: {e}")
            return False
    
    async def test_adapters(self) -> Dict[str, Any]:
        """어댑터 테스트"""
        results = {}
        
        try:
            # 투자 분석 어댑터 테스트
            investment_adapter = InvestmentA2AAdapter("websocket")
            investment_capabilities = AgentCapability(
                role=AgentRole.INVESTMENT_ANALYST,
                capabilities=["stock_analysis"],
                supported_tickers=["AAPL"],
                supported_timeframes=["1d"],
                max_concurrent_requests=1,
                response_time_avg=1.0,
                version="1.0.0"
            )
            investment_adapter.register_capabilities(investment_capabilities)
            results["investment_adapter"] = True
            
            # 리스크 분석 어댑터 테스트
            risk_adapter = RiskA2AAdapter("websocket")
            risk_capabilities = AgentCapability(
                role=AgentRole.RISK_ASSESSOR,
                capabilities=["risk_analysis"],
                supported_tickers=["AAPL"],
                supported_timeframes=["1d"],
                max_concurrent_requests=1,
                response_time_avg=1.0,
                version="1.0.0"
            )
            risk_adapter.register_capabilities(risk_capabilities)
            results["risk_adapter"] = True
            
            # 포트폴리오 관리 어댑터 테스트
            portfolio_adapter = PortfolioA2AAdapter("websocket")
            portfolio_capabilities = AgentCapability(
                role=AgentRole.PORTFOLIO_MANAGER,
                capabilities=["portfolio_analysis"],
                supported_tickers=["AAPL"],
                supported_timeframes=["1d"],
                max_concurrent_requests=1,
                response_time_avg=1.0,
                version="1.0.0"
            )
            portfolio_adapter.register_capabilities(portfolio_capabilities)
            results["portfolio_adapter"] = True
            
            return results
            
        except Exception as e:
            logger.error(f"Adapter test failed: {e}")
            return {"error": str(e)}
    
    async def test_integration_manager(self) -> bool:
        """통합 관리자 테스트"""
        try:
            # 통합 관리자 초기화
            await self.integration_manager.initialize()
            
            # 상태 조회 테스트
            status = await self.integration_manager.get_agent_status()
            assert status["initialized"] == True
            assert "adapters" in status
            assert len(status["adapters"]) >= 3
            
            # 종료
            await self.integration_manager.shutdown()
            
            return True
            
        except Exception as e:
            logger.error(f"Integration manager test failed: {e}")
            return False
    
    async def test_collaborative_analysis(self) -> Dict[str, Any]:
        """협업 분석 테스트"""
        try:
            # 통합 관리자 초기화
            await self.integration_manager.initialize()
            
            # AAPL에 대한 협업 분석 실행
            result = await self.integration_manager.start_collaborative_analysis(
                "AAPL", "test_user", "comprehensive"
            )
            
            # 결과 검증
            assert "ticker" in result
            assert result["ticker"] == "AAPL"
            assert "timestamp" in result
            assert "agents_used" in result
            assert "integrated_score" in result
            assert "recommendations" in result
            
            # 종료
            await self.integration_manager.shutdown()
            
            return {
                "success": True,
                "ticker": result["ticker"],
                "agents_used": result["agents_used"],
                "integrated_score": result["integrated_score"],
                "recommendations_count": len(result["recommendations"])
            }
            
        except Exception as e:
            logger.error(f"Collaborative analysis test failed: {e}")
            return {"error": str(e)}
    
    async def test_error_handling(self) -> bool:
        """에러 처리 테스트"""
        try:
            protocol = A2AProtocol("test_agent", AgentRole.INVESTMENT_ANALYST)
            
            # 잘못된 메시지 처리 테스트
            invalid_message = A2AMessage(
                message_id="test",
                sender_id="sender",
                receiver_id="receiver",
                message_type=MessageType.ERROR,
                priority=Priority.HIGH,
                timestamp=datetime.now(),
                payload={"error": "test_error"}
            )
            
            # 에러 응답 생성 테스트
            error_response = protocol.create_error_response(
                invalid_message, "Test error", "TEST_ERROR"
            )
            
            assert error_response.message_type == MessageType.ERROR
            assert error_response.payload["error_code"] == "TEST_ERROR"
            assert error_response.payload["error_message"] == "Test error"
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling test failed: {e}")
            return False
    
    async def test_performance(self) -> Dict[str, Any]:
        """성능 테스트"""
        try:
            # 통합 관리자 초기화
            await self.integration_manager.initialize()
            
            # 다중 요청 성능 테스트
            tickers = ["AAPL", "GOOGL", "MSFT"]
            start_time = time.time()
            
            tasks = []
            for ticker in tickers:
                task = self.integration_manager.start_collaborative_analysis(
                    ticker, f"test_user_{ticker}", "comprehensive"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # 성능 메트릭 계산
            total_time = end_time - start_time
            avg_time_per_analysis = total_time / len(tickers)
            successful_analyses = len([r for r in results if not isinstance(r, Exception)])
            
            # 종료
            await self.integration_manager.shutdown()
            
            return {
                "total_time": total_time,
                "avg_time_per_analysis": avg_time_per_analysis,
                "successful_analyses": successful_analyses,
                "total_requests": len(tickers),
                "success_rate": successful_analyses / len(tickers)
            }
            
        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            return {"error": str(e)}
    
    async def test_external_integration(self) -> Dict[str, Any]:
        """외부 연동 테스트"""
        try:
            # 통합 관리자 초기화
            await self.integration_manager.initialize()
            
            # 외부 에이전트 등록 시뮬레이션
            external_agents = [
                {
                    "agent_id": "external_analyst_001",
                    "endpoint": "ws://localhost:9001",
                    "role": AgentRole.MARKET_RESEARCHER
                },
                {
                    "agent_id": "external_risk_001", 
                    "endpoint": "ws://localhost:9002",
                    "role": AgentRole.RISK_ASSESSOR
                }
            ]
            
            # 외부 에이전트 등록 시도 (실제 연결은 실패할 수 있음)
            await self.integration_manager.register_with_external_agents(external_agents)
            
            # 외부 요청 처리 테스트
            external_request = {
                "type": "stock_analysis",
                "ticker": "TSLA",
                "user_id": "external_user"
            }
            
            response = await self.integration_manager.handle_external_request(external_request)
            
            # 종료
            await self.integration_manager.shutdown()
            
            return {
                "external_agents_registered": len(external_agents),
                "external_request_handled": "ticker" in response,
                "response_contains_analysis": "integrated_score" in response
            }
            
        except Exception as e:
            logger.error(f"External integration test failed: {e}")
            return {"error": str(e)}
    
    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("📊 A2A 연동 테스트 결과 요약")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r["status"] == "PASSED"])
        failed_tests = len([r for r in self.test_results.values() if r["status"] == "FAILED"])
        error_tests = len([r for r in self.test_results.values() if r["status"] == "ERROR"])
        
        total_duration = sum(r["duration"] for r in self.test_results.values())
        
        print(f"총 테스트: {total_tests}")
        print(f"✅ 성공: {passed_tests}")
        print(f"❌ 실패: {failed_tests}")
        print(f"💥 에러: {error_tests}")
        print(f"⏱️  총 소요 시간: {total_duration:.2f}초")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"📈 성공률: {success_rate:.1f}%")
        
        print(f"\n📋 상세 결과:")
        for test_name, result in self.test_results.items():
            status_emoji = {
                "PASSED": "✅",
                "FAILED": "❌", 
                "ERROR": "💥"
            }.get(result["status"], "❓")
            
            print(f"  {status_emoji} {test_name}: {result['status']} ({result['duration']:.2f}s)")
            if result["status"] != "PASSED" and "details" in result:
                details = result["details"]
                if "error" in details:
                    print(f"    에러: {details['error']}")
                elif isinstance(details, dict):
                    for key, value in details.items():
                        print(f"    {key}: {value}")
        
        # 성능 메트릭 출력
        if "성능 테스트" in self.test_results:
            perf_result = self.test_results["성능 테스트"]["details"]
            if "error" not in perf_result:
                print(f"\n⚡ 성능 메트릭:")
                print(f"  평균 분석 시간: {perf_result.get('avg_time_per_analysis', 0):.2f}초")
                print(f"  성공률: {perf_result.get('success_rate', 0)*100:.1f}%")
        
        print("\n" + "=" * 60)

class A2ADemo:
    """A2A 연동 데모"""
    
    def __init__(self):
        self.integration_manager = A2AIntegrationManager()
    
    async def run_demo(self):
        """A2A 연동 데모 실행"""
        print("🎭 A2A 연동 데모 시작")
        print("=" * 50)
        
        try:
            # 1. 초기화
            print("🔧 A2A 연동 초기화 중...")
            await self.integration_manager.initialize()
            
            # 2. 상태 조회
            print("\n📊 에이전트 상태 조회:")
            status = await self.integration_manager.get_agent_status()
            print(f"  초기화 상태: {status['initialized']}")
            print(f"  활성 어댑터: {len(status['adapters'])}")
            for adapter_name, adapter_info in status['adapters'].items():
                print(f"    - {adapter_name}: {adapter_info['role']}")
            
            # 3. AAPL 협업 분석
            print(f"\n🔍 AAPL 협업 분석 실행:")
            result = await self.integration_manager.start_collaborative_analysis(
                "AAPL", "demo_user", "comprehensive"
            )
            
            if "error" not in result:
                print(f"  ✅ 분석 완료")
                print(f"  📈 통합 점수: {result.get('integrated_score', 0):.1f}")
                print(f"  🤖 사용된 에이전트: {', '.join(result.get('agents_used', []))}")
                print(f"  💡 추천 수: {len(result.get('recommendations', []))}")
                
                # 추천 출력
                recommendations = result.get('recommendations', [])
                if recommendations:
                    print(f"  📋 주요 추천:")
                    for i, rec in enumerate(recommendations[:3], 1):
                        action = rec.get('action', 'N/A')
                        confidence = rec.get('confidence', 'N/A')
                        print(f"    {i}. {action} (신뢰도: {confidence})")
            else:
                print(f"  ❌ 분석 실패: {result['error']}")
            
            # 4. TSLA 분석
            print(f"\n🔍 TSLA 협업 분석 실행:")
            result2 = await self.integration_manager.start_collaborative_analysis(
                "TSLA", "demo_user", "comprehensive"
            )
            
            if "error" not in result2:
                print(f"  ✅ 분석 완료")
                print(f"  📈 통합 점수: {result2.get('integrated_score', 0):.1f}")
                print(f"  🤖 사용된 에이전트: {', '.join(result2.get('agents_used', []))}")
            else:
                print(f"  ❌ 분석 실패: {result2['error']}")
            
            # 5. 종료
            print(f"\n🔚 A2A 연동 종료 중...")
            await self.integration_manager.shutdown()
            print(f"✅ 데모 완료!")
            
        except Exception as e:
            print(f"❌ 데모 실행 중 오류: {e}")
            await self.integration_manager.shutdown()

async def main():
    """메인 함수"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # 데모 모드
        demo = A2ADemo()
        await demo.run_demo()
    else:
        # 테스트 모드
        test_suite = A2ATestSuite()
        await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
