#!/usr/bin/env python3
"""
투자 성향 기반 주식 분석 AI 에이전트 데모
"""

import asyncio
import json
from agent_graph import investment_agent

async def demo_conservative_investor():
    """보수적 투자자 데모"""
    print("🔵 보수적 투자자 시나리오")
    print("=" * 50)
    
    user_id = "demo_conservative"
    
    # 1. 첫 번째 질문 (투자 성향 수집 시작)
    print("\n1️⃣ 첫 번째 질문")
    result = await investment_agent.process_query("안녕하세요, 주식 투자에 대해 조언해주세요.", user_id)
    print(f"AI: {result['message']}")
    print(f"질문: {result['question']['question']}")
    
    # 2. 보수적 답변들
    from memory_manager import memory_manager
    
    answers = [
        ("risk_tolerance", "conservative", "보수적 - 안정적인 수익을 원합니다"),
        ("investment_horizon", "long_term", "장기 - 6개월 이상 투자합니다"),
        ("trading_style", "value_investing", "가치 투자 - 기업의 내재가치를 분석합니다"),
        ("sectors", "technology,healthcare", "기술, 헬스케어 섹터에 관심이 있습니다")
    ]
    
    for i, (step, answer, description) in enumerate(answers, 2):
        print(f"\n{i}️⃣ {description}")
        result = memory_manager.process_profile_answer(user_id, step, answer)
        print(f"AI: {result['message']}")
        
        if result.get('profile_completed'):
            print(f"\n✅ 프로필 완성!")
            profile = result['profile_summary']
            print(f"   리스크 성향: {profile['risk_tolerance']}")
            print(f"   투자 기간: {profile['investment_horizon']}")
            print(f"   거래 스타일: {profile['trading_style']}")
            print(f"   선호 섹터: {', '.join(profile['preferred_sectors'])}")
            break
    
    # 3. AAPL 분석 요청
    print(f"\n3️⃣ AAPL 분석 요청")
    result = await investment_agent.process_query("AAPL 분석해줘", user_id)
    
    if result['type'] == 'analysis':
        analysis = result['analysis']
        recommendation = result['recommendation']
        
        print(f"AI: {result['content']}")
        print(f"\n📊 분석 결과:")
        print(f"   현재가: ${analysis.current_price:.2f} {analysis.currency}")
        print(f"   종합 점수: {analysis.overall_score:.1f}/100")
        print(f"   리스크 점수: {analysis.risk_score:.1f}/100")
        
        # 리스크 이벤트 분석 결과 출력
        if analysis.risk_event_analysis:
            print(f"\n⚠️  리스크 이벤트 분석:")
            print(f"   리스크 레벨: {analysis.risk_event_analysis.risk_level}")
            print(f"   리스크 점수: {analysis.risk_event_analysis.risk_score}/100")
            print(f"   최근 이벤트: {analysis.risk_event_analysis.recent_events_count}개")
            print(f"   고위험 이벤트: {analysis.risk_event_analysis.high_risk_events_count}개")
            if analysis.risk_event_analysis.risk_factors:
                print(f"   주요 리스크: {', '.join(analysis.risk_event_analysis.risk_factors)}")
        
        print(f"\n💡 추천:")
        print(f"   액션: {recommendation['recommendation']}")
        print(f"   신뢰도: {recommendation['confidence']}%")
        print(f"   매수 범위: ${recommendation['buy_price_range']['lower']:.2f} - ${recommendation['buy_price_range']['upper']:.2f}")
        print(f"   손절매: ${recommendation['stop_loss']:.2f}")

async def demo_aggressive_investor():
    """공격적 투자자 데모"""
    print("\n\n🔴 공격적 투자자 시나리오")
    print("=" * 50)
    
    user_id = "demo_aggressive"
    
    # 빠른 프로필 생성 (데모용)
    from investment_profile import InvestmentProfileBuilder, RiskTolerance, InvestmentHorizon, TradingStyle
    from memory_manager import memory_manager
    
    builder = InvestmentProfileBuilder(user_id)
    profile = (builder
               .set_risk_tolerance(RiskTolerance.AGGRESSIVE)
               .set_investment_horizon(InvestmentHorizon.SHORT_TERM)
               .set_trading_style(TradingStyle.DAY_TRADING)
               .add_preferred_sector("technology")
               .build())
    
    memory_manager.save_user_profile(profile)
    print(f"프로필 생성: {profile.risk_tolerance.value} / {profile.trading_style.value}")
    
    # TSLA 분석 요청
    print(f"\n1️⃣ TSLA 분석 요청")
    result = await investment_agent.process_query("TSLA 분석해줘", user_id)
    
    if result['type'] == 'analysis':
        analysis = result['analysis']
        recommendation = result['recommendation']
        
        print(f"AI: {result['content']}")
        print(f"\n📊 분석 결과:")
        print(f"   현재가: ${analysis.current_price:.2f} {analysis.currency}")
        print(f"   종합 점수: {analysis.overall_score:.1f}/100")
        print(f"   모멘텀 점수: {analysis.momentum_score:.1f}/100")
        
        # 리스크 이벤트 분석 결과 출력
        if analysis.risk_event_analysis:
            print(f"\n⚠️  리스크 이벤트 분석:")
            print(f"   리스크 레벨: {analysis.risk_event_analysis.risk_level}")
            print(f"   리스크 점수: {analysis.risk_event_analysis.risk_score}/100")
            print(f"   최근 이벤트: {analysis.risk_event_analysis.recent_events_count}개")
            print(f"   고위험 이벤트: {analysis.risk_event_analysis.high_risk_events_count}개")
            if analysis.risk_event_analysis.risk_factors:
                print(f"   주요 리스크: {', '.join(analysis.risk_event_analysis.risk_factors)}")
        
        print(f"\n💡 추천:")
        print(f"   액션: {recommendation['recommendation']}")
        print(f"   신뢰도: {recommendation['confidence']}%")
        print(f"   매수 범위: ${recommendation['buy_price_range']['lower']:.2f} - ${recommendation['buy_price_range']['upper']:.2f}")
        print(f"   익절매: ${recommendation['take_profit']:.2f}")

async def main():
    """메인 데모 함수"""
    print("🚀 투자 성향 기반 주식 분석 AI 에이전트 데모")
    print("=" * 60)
    
    try:
        # 보수적 투자자 데모
        await demo_conservative_investor()
        
        # 공격적 투자자 데모
        await demo_aggressive_investor()
        
        print(f"\n\n✅ 데모 완료!")
        print(f"💡 이제 Cursor에서 다음과 같이 사용할 수 있습니다:")
        print(f"   /stock-agent.ask_stock_agent \"AAPL 분석해줘\" user_id=my_user")
        print(f"   /stock-agent.get_user_profile user_id=my_user")
        
    except Exception as e:
        print(f"\n❌ 데모 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

