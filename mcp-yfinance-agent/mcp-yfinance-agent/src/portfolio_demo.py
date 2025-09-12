#!/usr/bin/env python3
"""
포트폴리오 추적 및 분석 데모 스크립트
"""

import asyncio
import json
from portfolio_manager import portfolio_manager
from portfolio_analyzer import portfolio_analyzer
from memory_manager import memory_manager
from investment_profile import InvestmentProfileBuilder, RiskTolerance, InvestmentHorizon, TradingStyle

async def demo_portfolio_management():
    """포트폴리오 관리 데모"""
    print("📊 포트폴리오 관리 데모")
    print("=" * 50)
    
    user_id = "demo_portfolio_user"
    
    # 1. 투자 성향 프로필 생성
    print("\n1️⃣ 투자 성향 프로필 생성")
    builder = InvestmentProfileBuilder(user_id)
    profile = (builder
               .set_risk_tolerance(RiskTolerance.MODERATE)
               .set_investment_horizon(InvestmentHorizon.MEDIUM_TERM)
               .set_trading_style(TradingStyle.SWING_TRADING)
               .add_preferred_sector("technology")
               .add_preferred_sector("healthcare")
               .build())
    
    memory_manager.save_user_profile(profile)
    print(f"✅ 프로필 생성: {profile.risk_tolerance.value} / {profile.trading_style.value}")
    
    # 2. 포지션 추가
    print("\n2️⃣ 포지션 추가")
    
    positions = [
        ("AAPL", 10, 150.0, "USD", "technology"),
        ("TSLA", 5, 200.0, "USD", "technology"),
        ("JNJ", 20, 160.0, "USD", "healthcare"),
        ("MSFT", 8, 300.0, "USD", "technology")
    ]
    
    for ticker, quantity, avg_price, currency, sector in positions:
        position = portfolio_manager.add_position(user_id, ticker, quantity, avg_price, currency, sector)
        print(f"   {ticker}: {quantity}주 @ ${avg_price:.2f} (섹터: {sector})")
    
    # 3. 포트폴리오 요약
    print("\n3️⃣ 포트폴리오 요약")
    summary = portfolio_manager.get_portfolio_summary(user_id)
    print(f"   총 투자금액: ${summary['total_invested']:,.2f}")
    print(f"   현재 시장가치: ${summary['total_market_value']:,.2f}")
    print(f"   미실현 손익: ${summary['total_unrealized_pnl']:,.2f} ({summary['total_unrealized_pnl_percent']:.2f}%)")
    print(f"   보유 종목 수: {summary['total_positions']}개")
    
    # 섹터 할당
    print(f"\n   섹터 할당:")
    for sector, allocation in summary['sector_allocation'].items():
        print(f"     {sector}: {allocation:.1f}%")
    
    # 4. 포지션 목록
    print("\n4️⃣ 포지션 상세")
    positions_list = portfolio_manager.get_positions_list(user_id)
    for pos in positions_list:
        print(f"   {pos['ticker']}: {pos['quantity']}주")
        print(f"     평단가: ${pos['average_price']:.2f}")
        print(f"     현재가: ${pos['current_price']:.2f}")
        print(f"     시장가치: ${pos['market_value']:,.2f}")
        print(f"     손익: ${pos['unrealized_pnl']:,.2f} ({pos['unrealized_pnl_percent']:.2f}%)")
        print(f"     섹터: {pos['sector']}")
        print()
    
    # 5. 포트폴리오 분석
    print("\n5️⃣ 포트폴리오 종합 분석")
    analysis = portfolio_analyzer.analyze_portfolio(user_id, profile)
    
    print(f"   📈 성과 메트릭:")
    perf = analysis.performance_metrics
    print(f"     전체 수익률: {perf['total_return_percent']:.2f}%")
    print(f"     승률: {perf['win_rate']:.1f}%")
    print(f"     평균 수익률: {perf['average_return_percent']:.2f}%")
    print(f"     최고 수익률: {perf['max_gain_percent']:.2f}%")
    print(f"     최대 손실률: {perf['max_loss_percent']:.2f}%")
    
    print(f"\n   ⚠️ 리스크 메트릭:")
    risk = analysis.risk_metrics
    print(f"     포트폴리오 집중도: {risk['portfolio_concentration']:.1f}%")
    print(f"     최대 포지션 비중: {risk['max_position_weight']:.1f}%")
    print(f"     섹터 집중도: {risk['sector_concentration']:.1f}%")
    print(f"     손실 포지션 비율: {risk['loss_ratio']:.1f}%")
    
    # 6. 포트폴리오 추천
    print(f"\n6️⃣ 포트폴리오 추천")
    for rec in analysis.recommendations:
        priority_emoji = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
        print(f"   {priority_emoji} {rec['type'].upper()}: {rec['message']}")
        print(f"     액션: {rec['action']}")
    
    # 7. 개별 포지션 추천
    print(f"\n7️⃣ 개별 포지션 추천")
    for pos_analysis in analysis.positions_analysis:
        ticker = pos_analysis['ticker']
        rec = pos_analysis['recommendation']
        
        print(f"   {ticker}:")
        print(f"     추천 액션: {rec['action']}")
        print(f"     신뢰도: {rec['confidence']:.1f}%")
        print(f"     추천 이유: {rec['reasoning']}")
        if rec['stop_loss']:
            print(f"     손절매: ${rec['stop_loss']:.2f}")
        if rec['take_profit']:
            print(f"     익절매: ${rec['take_profit']:.2f}")
        print()
    
    # 8. 특정 포지션 추천 조회
    print("\n8️⃣ 특정 포지션 추천 조회 (AAPL)")
    aapl_rec = portfolio_analyzer.get_position_recommendation(user_id, "AAPL", profile)
    if aapl_rec:
        print(f"   AAPL 추천: {aapl_rec.recommendation}")
        print(f"   신뢰도: {aapl_rec.confidence:.1f}%")
        print(f"   추천 이유: {aapl_rec.reasoning}")
        print(f"   현재 손익: ${aapl_rec.current_position.unrealized_pnl:,.2f} ({aapl_rec.current_position.unrealized_pnl_percent:.2f}%)")
    
    # 9. 포지션 제거 데모
    print("\n9️⃣ 포지션 제거 데모 (JNJ)")
    removed = portfolio_manager.remove_position(user_id, "JNJ")
    if removed:
        print(f"   JNJ 포지션 제거 완료")
        print(f"   최종 손익: ${removed.unrealized_pnl:,.2f} ({removed.unrealized_pnl_percent:.2f}%)")
    
    # 10. 최종 포트폴리오 상태
    print("\n🔟 최종 포트폴리오 상태")
    final_summary = portfolio_manager.get_portfolio_summary(user_id)
    print(f"   보유 종목 수: {final_summary['total_positions']}개")
    print(f"   총 투자금액: ${final_summary['total_invested']:,.2f}")
    print(f"   현재 시장가치: ${final_summary['total_market_value']:,.2f}")
    print(f"   미실현 손익: ${final_summary['total_unrealized_pnl']:,.2f} ({final_summary['total_unrealized_pnl_percent']:.2f}%)")

async def main():
    """메인 데모 함수"""
    print("🚀 포트폴리오 추적 및 분석 데모 시작")
    print("=" * 60)
    
    try:
        await demo_portfolio_management()
        
        print(f"\n\n✅ 포트폴리오 데모 완료!")
        print(f"💡 이제 Cursor에서 다음과 같이 사용할 수 있습니다:")
        print(f"   /stock-agent.add_position user_id=my_user ticker=AAPL quantity=10 average_price=150.0")
        print(f"   /stock-agent.get_portfolio_summary user_id=my_user")
        print(f"   /stock-agent.analyze_portfolio user_id=my_user")
        print(f"   /stock-agent.get_position_recommendation user_id=my_user ticker=AAPL")
        
    except Exception as e:
        print(f"\n❌ 데모 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
