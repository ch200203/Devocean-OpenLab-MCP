#!/usr/bin/env python3
"""
리스크 이벤트 감지 에이전트 테스트 스크립트
"""

import asyncio
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_risk_event_server import detector

async def test_risk_agent():
    """리스크 에이전트 테스트"""
    print("🧪 리스크 이벤트 감지 에이전트 테스트")
    print("=" * 50)
    
    # 테스트할 종목들
    test_tickers = ["AAPL", "TSLA", "GOOGL"]
    
    for ticker in test_tickers:
        print(f"\n📊 {ticker} 리스크 분석")
        print("-" * 30)
        
        try:
            # 리스크 분석 실행
            analysis = detector.analyze_ticker_risk(ticker)
            
            print(f"종목: {analysis.ticker}")
            print(f"전체 리스크 점수: {analysis.overall_risk_score}/100")
            print(f"리스크 레벨: {analysis.risk_level}")
            print(f"총 이벤트 수: {analysis.total_events}")
            print(f"고위험 이벤트: {analysis.high_risk_events}")
            print(f"추천: {analysis.recommendation}")
            
            if analysis.risk_factors:
                print(f"리스크 팩터: {', '.join(analysis.risk_factors)}")
            
            print(f"\n최근 이벤트 ({len(analysis.recent_events)}개):")
            for i, event in enumerate(analysis.recent_events[:3], 1):
                print(f"  {i}. {event.title}")
                print(f"     타입: {event.event_type}, 심각도: {event.severity}")
                print(f"     리스크 점수: {event.risk_score}/100")
                print(f"     출처: {event.source}")
                print()
            
        except Exception as e:
            print(f"❌ {ticker} 분석 중 오류: {e}")
    
    print("\n✅ 테스트 완료!")

async def test_risk_agent_integration():
    """통합 에이전트 테스트"""
    print("\n🔗 통합 에이전트 테스트")
    print("=" * 50)
    
    try:
        from agent_graph import investment_agent
        
        user_id = "test_user"
        
        # 간단한 프로필 생성
        from investment_profile import InvestmentProfileBuilder, RiskTolerance, InvestmentHorizon, TradingStyle
        from memory_manager import memory_manager
        
        builder = InvestmentProfileBuilder(user_id)
        profile = (builder
                   .set_risk_tolerance(RiskTolerance.MODERATE)
                   .set_investment_horizon(InvestmentHorizon.SHORT_TERM)
                   .set_trading_style(TradingStyle.SWING_TRADING)
                   .add_preferred_sector("technology")
                   .build())
        
        memory_manager.save_user_profile(profile)
        print(f"프로필 생성 완료: {profile.risk_tolerance.value}")
        
        # AAPL 분석 요청
        print(f"\n📈 AAPL 분석 요청")
        result = await investment_agent.process_query("AAPL 분석해줘", user_id)
        
        if result['type'] == 'analysis':
            analysis = result['analysis']
            recommendation = result['recommendation']
            
            print(f"AI 응답: {result['content'][:200]}...")
            print(f"\n분석 결과:")
            print(f"  현재가: ${analysis.current_price:.2f}")
            print(f"  종합 점수: {analysis.overall_score:.1f}/100")
            
            # 리스크 이벤트 분석 결과
            if analysis.risk_event_analysis:
                print(f"\n⚠️  리스크 이벤트 분석:")
                print(f"  리스크 레벨: {analysis.risk_event_analysis.risk_level}")
                print(f"  리스크 점수: {analysis.risk_event_analysis.risk_score}/100")
                print(f"  최근 이벤트: {analysis.risk_event_analysis.recent_events_count}개")
                print(f"  고위험 이벤트: {analysis.risk_event_analysis.high_risk_events_count}개")
            
            print(f"\n추천:")
            print(f"  액션: {recommendation['recommendation']}")
            print(f"  신뢰도: {recommendation['confidence']}%")
        
        print("\n✅ 통합 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 통합 테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """메인 테스트 함수"""
    print("🚀 리스크 이벤트 감지 에이전트 테스트 시작")
    print("=" * 60)
    
    # 1. 리스크 에이전트 단독 테스트
    await test_risk_agent()
    
    # 2. 통합 에이전트 테스트
    await test_risk_agent_integration()
    
    print(f"\n🎉 모든 테스트 완료!")
    print(f"💡 이제 다음과 같이 사용할 수 있습니다:")
    print(f"   python demo.py  # 전체 데모 실행")
    print(f"   python agent_graph.py  # 에이전트 직접 실행")

if __name__ == "__main__":
    asyncio.run(main())
