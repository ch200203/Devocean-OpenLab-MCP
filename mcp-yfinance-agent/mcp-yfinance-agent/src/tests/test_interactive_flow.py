#!/usr/bin/env python3
"""
투자 성향 기반 대화형 플로우 테스트 스크립트
"""

import asyncio
import json
from agent_graph import investment_agent
from memory_manager import memory_manager

async def test_profile_collection():
    """투자 성향 수집 테스트"""
    print("=== 투자 성향 수집 테스트 ===")
    
    user_id = "test_user_001"
    
    # 1. 첫 번째 질문 시작
    result = await investment_agent.process_query("안녕하세요, 주식 투자에 대해 조언해주세요.", user_id)
    print(f"1. 첫 질문: {result['message']}")
    print(f"   질문: {result['question']['question']}")
    print(f"   옵션: {json.dumps(result['question']['options'], ensure_ascii=False, indent=2)}")
    
    # 2. 리스크 성향 답변
    answer_result = memory_manager.process_profile_answer(user_id, "risk_tolerance", "conservative")
    print(f"\n2. 리스크 성향 답변 (conservative): {answer_result['message']}")
    if answer_result.get('next_question'):
        print(f"   다음 질문: {answer_result['next_question']['question']}")
    
    # 3. 투자 기간 답변
    answer_result = memory_manager.process_profile_answer(user_id, "investment_horizon", "medium_term")
    print(f"\n3. 투자 기간 답변 (medium_term): {answer_result['message']}")
    if answer_result.get('next_question'):
        print(f"   다음 질문: {answer_result['next_question']['question']}")
    
    # 4. 거래 스타일 답변
    answer_result = memory_manager.process_profile_answer(user_id, "trading_style", "swing_trading")
    print(f"\n4. 거래 스타일 답변 (swing_trading): {answer_result['message']}")
    if answer_result.get('next_question'):
        print(f"   다음 질문: {answer_result['next_question']['question']}")
    
    # 5. 섹터 선호도 답변
    answer_result = memory_manager.process_profile_answer(user_id, "sectors", "technology,healthcare")
    print(f"\n5. 섹터 선호도 답변 (technology,healthcare): {answer_result['message']}")
    
    if answer_result.get('profile_completed'):
        print(f"\n✅ 프로필 완성!")
        print(f"   프로필 요약: {json.dumps(answer_result['profile_summary'], ensure_ascii=False, indent=2)}")

async def test_stock_analysis():
    """종목 분석 테스트"""
    print("\n=== 종목 분석 테스트 ===")
    
    user_id = "test_user_001"
    
    # AAPL 분석 요청
    result = await investment_agent.process_query("AAPL 분석해줘", user_id)
    
    if result['type'] == 'analysis':
        print(f"분석 결과: {result['content']}")
        print(f"\n종목 분석 상세:")
        analysis = result['analysis']
        print(f"  - 현재가: ${analysis.current_price:.2f} {analysis.currency}")
        print(f"  - 종합 점수: {analysis.overall_score:.1f}/100")
        print(f"  - 리스크 점수: {analysis.risk_score:.1f}/100")
        print(f"  - 모멘텀 점수: {analysis.momentum_score:.1f}/100")
        print(f"  - 추세 점수: {analysis.trend_score:.1f}/100")
        
        print(f"\n추천 결과:")
        recommendation = result['recommendation']
        print(f"  - 추천 액션: {recommendation['recommendation']}")
        print(f"  - 신뢰도: {recommendation['confidence']}%")
        print(f"  - 매수 가격 범위: ${recommendation['buy_price_range']['lower']:.2f} - ${recommendation['buy_price_range']['upper']:.2f}")
        print(f"  - 매도 가격 범위: ${recommendation['sell_price_range']['lower']:.2f} - ${recommendation['sell_price_range']['upper']:.2f}")
        print(f"  - 손절매: ${recommendation['stop_loss']:.2f}")
        print(f"  - 익절매: ${recommendation['take_profit']:.2f}")
        print(f"  - 추천 이유: {recommendation['reasoning']}")

async def test_different_profiles():
    """다른 투자 성향 테스트"""
    print("\n=== 다른 투자 성향 테스트 ===")
    
    # 공격적 투자자 프로필 생성
    user_id_aggressive = "test_user_002"
    
    # 빠른 프로필 생성 (테스트용)
    from investment_profile import InvestmentProfileBuilder, RiskTolerance, InvestmentHorizon, TradingStyle
    from memory_manager import memory_manager
    
    builder = InvestmentProfileBuilder(user_id_aggressive)
    profile = (builder
               .set_risk_tolerance(RiskTolerance.AGGRESSIVE)
               .set_investment_horizon(InvestmentHorizon.SHORT_TERM)
               .set_trading_style(TradingStyle.DAY_TRADING)
               .add_preferred_sector("technology")
               .build())
    
    memory_manager.save_user_profile(profile)
    print(f"공격적 투자자 프로필 생성 완료: {profile.risk_tolerance.value}")
    
    # TSLA 분석 요청
    result = await investment_agent.process_query("TSLA 분석해줘", user_id_aggressive)
    
    if result['type'] == 'analysis':
        print(f"\n공격적 투자자를 위한 TSLA 분석:")
        recommendation = result['recommendation']
        print(f"  - 추천 액션: {recommendation['recommendation']}")
        print(f"  - 신뢰도: {recommendation['confidence']}%")
        print(f"  - 매수 가격 범위: ${recommendation['buy_price_range']['lower']:.2f} - ${recommendation['buy_price_range']['upper']:.2f}")
        print(f"  - 매도 가격 범위: ${recommendation['sell_price_range']['lower']:.2f} - ${recommendation['sell_price_range']['upper']:.2f}")

async def main():
    """메인 테스트 함수"""
    print("🚀 투자 성향 기반 AI 에이전트 테스트 시작\n")
    
    try:
        # 1. 투자 성향 수집 테스트
        await test_profile_collection()
        
        # 2. 종목 분석 테스트
        await test_stock_analysis()
        
        # 3. 다른 투자 성향 테스트
        await test_different_profiles()
        
        print("\n✅ 모든 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

