from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import yfinance as yf
from portfolio_manager import Portfolio, Position, portfolio_manager
from investment_profile import InvestmentProfile
from personalized_analyzer import PersonalizedStockAnalyzer, StockAnalysis

@dataclass
class PortfolioAnalysis:
    """포트폴리오 분석 결과"""
    user_id: str
    total_invested: float
    total_market_value: float
    total_unrealized_pnl: float
    total_unrealized_pnl_percent: float
    sector_allocation: Dict[str, float]
    risk_metrics: Dict[str, float]
    performance_metrics: Dict[str, float]
    recommendations: List[Dict[str, Any]]
    positions_analysis: List[Dict[str, Any]]
    last_updated: datetime

@dataclass
class PositionRecommendation:
    """포지션별 추천"""
    ticker: str
    current_position: Position
    stock_analysis: StockAnalysis
    recommendation: str  # HOLD, BUY_MORE, SELL_PARTIAL, SELL_ALL
    confidence: float
    reasoning: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class PortfolioAnalyzer:
    """포트폴리오 분석기"""
    
    def __init__(self):
        self.stock_analyzer = PersonalizedStockAnalyzer()
    
    def analyze_portfolio(self, user_id: str, profile: Optional[InvestmentProfile] = None) -> PortfolioAnalysis:
        """포트폴리오 종합 분석"""
        portfolio = portfolio_manager.get_portfolio(user_id)
        
        # 현재가 업데이트
        self._update_portfolio_prices(portfolio)
        
        # 리스크 메트릭 계산
        risk_metrics = self._calculate_risk_metrics(portfolio, profile)
        
        # 성과 메트릭 계산
        performance_metrics = self._calculate_performance_metrics(portfolio)
        
        # 포지션별 분석
        positions_analysis = self._analyze_positions(portfolio, user_id, profile)
        
        # 포트폴리오 추천
        recommendations = self._generate_portfolio_recommendations(portfolio, profile, positions_analysis)
        
        return PortfolioAnalysis(
            user_id=user_id,
            total_invested=portfolio.total_invested,
            total_market_value=portfolio.total_market_value,
            total_unrealized_pnl=portfolio.total_unrealized_pnl,
            total_unrealized_pnl_percent=portfolio.total_unrealized_pnl_percent,
            sector_allocation=portfolio.get_sector_allocation(),
            risk_metrics=risk_metrics,
            performance_metrics=performance_metrics,
            recommendations=recommendations,
            positions_analysis=positions_analysis,
            last_updated=datetime.now()
        )
    
    def _update_portfolio_prices(self, portfolio: Portfolio):
        """포트폴리오의 모든 종목 현재가 업데이트"""
        for ticker in portfolio.positions.keys():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    portfolio.update_position(ticker, current_price)
            except Exception as e:
                print(f"종목 {ticker} 현재가 업데이트 실패: {e}")
    
    def _calculate_risk_metrics(self, portfolio: Portfolio, profile: Optional[InvestmentProfile]) -> Dict[str, float]:
        """리스크 메트릭 계산"""
        if not portfolio.positions:
            return {}
        
        # 포트폴리오 집중도 (Herfindahl Index)
        weights = [pos.market_value / portfolio.total_market_value for pos in portfolio.positions.values()]
        concentration = sum(w**2 for w in weights) * 100
        
        # 최대 포지션 비중
        max_position_weight = max(weights) * 100 if weights else 0
        
        # 섹터 집중도
        sector_allocation = portfolio.get_sector_allocation()
        sector_concentration = max(sector_allocation.values()) if sector_allocation else 0
        
        # 개별 종목 손실률
        loss_positions = [pos for pos in portfolio.positions.values() if pos.unrealized_pnl < 0]
        loss_ratio = len(loss_positions) / len(portfolio.positions) * 100 if portfolio.positions else 0
        
        # 최대 손실률
        max_loss = min(pos.unrealized_pnl_percent for pos in portfolio.positions.values()) if portfolio.positions else 0
        
        return {
            "portfolio_concentration": concentration,
            "max_position_weight": max_position_weight,
            "sector_concentration": sector_concentration,
            "loss_ratio": loss_ratio,
            "max_loss_percent": max_loss,
            "total_positions": len(portfolio.positions)
        }
    
    def _calculate_performance_metrics(self, portfolio: Portfolio) -> Dict[str, float]:
        """성과 메트릭 계산"""
        if not portfolio.positions:
            return {}
        
        # 전체 수익률
        total_return = portfolio.total_unrealized_pnl_percent
        
        # 승률 (수익 포지션 비율)
        profitable_positions = [pos for pos in portfolio.positions.values() if pos.unrealized_pnl > 0]
        win_rate = len(profitable_positions) / len(portfolio.positions) * 100 if portfolio.positions else 0
        
        # 평균 수익률
        avg_return = sum(pos.unrealized_pnl_percent for pos in portfolio.positions.values()) / len(portfolio.positions) if portfolio.positions else 0
        
        # 최고 수익률
        max_gain = max(pos.unrealized_pnl_percent for pos in portfolio.positions.values()) if portfolio.positions else 0
        
        # 최대 손실률
        max_loss = min(pos.unrealized_pnl_percent for pos in portfolio.positions.values()) if portfolio.positions else 0
        
        return {
            "total_return_percent": total_return,
            "win_rate": win_rate,
            "average_return_percent": avg_return,
            "max_gain_percent": max_gain,
            "max_loss_percent": max_loss,
            "profit_factor": abs(max_gain / max_loss) if max_loss != 0 else 0
        }
    
    def _analyze_positions(self, portfolio: Portfolio, user_id: str, 
                          profile: Optional[InvestmentProfile]) -> List[Dict[str, Any]]:
        """포지션별 분석"""
        positions_analysis = []
        
        for ticker, position in portfolio.positions.items():
            try:
                # 종목 분석
                stock_analysis = self.stock_analyzer.analyze_stock(ticker, user_id)
                
                if stock_analysis:
                    # 포지션별 추천 생성
                    recommendation = self._generate_position_recommendation(
                        position, stock_analysis, profile
                    )
                    
                    positions_analysis.append({
                        "ticker": ticker,
                        "position": {
                            "quantity": position.quantity,
                            "average_price": position.average_price,
                            "current_price": position.current_price,
                            "market_value": position.market_value,
                            "unrealized_pnl": position.unrealized_pnl,
                            "unrealized_pnl_percent": position.unrealized_pnl_percent,
                            "sector": position.sector
                        },
                        "stock_analysis": {
                            "overall_score": stock_analysis.overall_score,
                            "risk_score": stock_analysis.risk_score,
                            "momentum_score": stock_analysis.momentum_score,
                            "trend_score": stock_analysis.trend_score
                        },
                        "recommendation": recommendation
                    })
            except Exception as e:
                print(f"종목 {ticker} 분석 실패: {e}")
        
        return positions_analysis
    
    def _generate_position_recommendation(self, position: Position, 
                                        stock_analysis: StockAnalysis,
                                        profile: Optional[InvestmentProfile]) -> Dict[str, Any]:
        """포지션별 추천 생성"""
        # 기본 추천 로직
        recommendation = "HOLD"
        confidence = 50.0
        reasoning = []
        
        # 수익률 기반 추천
        if position.unrealized_pnl_percent > 20:
            if stock_analysis.momentum_score < 40:
                recommendation = "SELL_PARTIAL"
                confidence = 70.0
                reasoning.append("높은 수익률과 약한 모멘텀으로 부분 매도 추천")
        elif position.unrealized_pnl_percent < -15:
            if stock_analysis.overall_score > 60:
                recommendation = "BUY_MORE"
                confidence = 65.0
                reasoning.append("낮은 가격과 좋은 분석 점수로 추가 매수 추천")
            elif stock_analysis.overall_score < 30:
                recommendation = "SELL_ALL"
                confidence = 80.0
                reasoning.append("큰 손실과 나쁜 분석 점수로 전량 매도 추천")
        
        # 기술적 분석 기반 추천
        if stock_analysis.trend_score > 70 and position.unrealized_pnl_percent < 10:
            if recommendation == "HOLD":
                recommendation = "BUY_MORE"
                confidence = 60.0
                reasoning.append("강한 상승 추세로 추가 매수 추천")
        
        # 투자 성향별 조정
        if profile:
            if profile.risk_tolerance.value == "conservative":
                if position.unrealized_pnl_percent > 10:
                    recommendation = "SELL_PARTIAL"
                    confidence = min(confidence + 10, 90.0)
                    reasoning.append("보수적 투자자에게 높은 수익률에서 부분 매도 추천")
            elif profile.risk_tolerance.value == "aggressive":
                if position.unrealized_pnl_percent < -10 and stock_analysis.overall_score > 50:
                    recommendation = "BUY_MORE"
                    confidence = min(confidence + 10, 90.0)
                    reasoning.append("공격적 투자자에게 좋은 기회로 추가 매수 추천")
        
        # 손절/익절 가격 계산
        stop_loss = position.average_price * 0.95  # 5% 손절
        take_profit = position.average_price * 1.15  # 15% 익절
        
        if profile:
            stop_loss = position.average_price * (1 - profile.stop_loss_tolerance / 100)
            take_profit = position.average_price * (1 + profile.take_profit_target / 100)
        
        return {
            "action": recommendation,
            "confidence": confidence,
            "reasoning": " | ".join(reasoning) if reasoning else "현재 포지션 유지 추천",
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "target_price": take_profit if recommendation in ["SELL_PARTIAL", "SELL_ALL"] else None
        }
    
    def _generate_portfolio_recommendations(self, portfolio: Portfolio, 
                                          profile: Optional[InvestmentProfile],
                                          positions_analysis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """포트폴리오 전체 추천 생성"""
        recommendations = []
        
        # 포트폴리오 집중도 추천
        risk_metrics = self._calculate_risk_metrics(portfolio, profile)
        
        if risk_metrics.get("max_position_weight", 0) > 30:
            recommendations.append({
                "type": "diversification",
                "priority": "high",
                "message": f"최대 포지션 비중이 {risk_metrics['max_position_weight']:.1f}%로 과도합니다. 분산투자를 고려하세요.",
                "action": "포지션 비중 조정"
            })
        
        if risk_metrics.get("sector_concentration", 0) > 50:
            recommendations.append({
                "type": "sector_diversification",
                "priority": "medium",
                "message": f"특정 섹터에 {risk_metrics['sector_concentration']:.1f}% 집중되어 있습니다. 섹터 분산을 고려하세요.",
                "action": "다른 섹터 종목 추가"
            })
        
        # 손실 포지션 추천
        loss_positions = [pos for pos in positions_analysis if pos["position"]["unrealized_pnl"] < 0]
        if len(loss_positions) > len(positions_analysis) * 0.6:
            recommendations.append({
                "type": "loss_management",
                "priority": "high",
                "message": f"손실 포지션이 {len(loss_positions)}개로 많습니다. 손절매를 검토하세요.",
                "action": "손실 포지션 재검토"
            })
        
        # 투자 성향별 추천
        if profile:
            if profile.risk_tolerance.value == "conservative":
                if portfolio.total_unrealized_pnl_percent > 15:
                    recommendations.append({
                        "type": "profit_taking",
                        "priority": "medium",
                        "message": "보수적 투자자에게 높은 수익률입니다. 일부 익절을 고려하세요.",
                        "action": "부분 익절"
                    })
            elif profile.risk_tolerance.value == "aggressive":
                if portfolio.total_unrealized_pnl_percent < -10:
                    recommendations.append({
                        "type": "opportunity",
                        "priority": "medium",
                        "message": "공격적 투자자에게 좋은 매수 기회일 수 있습니다.",
                        "action": "추가 투자 검토"
                    })
        
        return recommendations
    
    def get_position_recommendation(self, user_id: str, ticker: str, 
                                  profile: Optional[InvestmentProfile] = None) -> Optional[PositionRecommendation]:
        """특정 포지션 추천"""
        position = portfolio_manager.get_position(user_id, ticker)
        if not position:
            return None
        
        stock_analysis = self.stock_analyzer.analyze_stock(ticker, user_id)
        if not stock_analysis:
            return None
        
        recommendation_data = self._generate_position_recommendation(position, stock_analysis, profile)
        
        return PositionRecommendation(
            ticker=ticker,
            current_position=position,
            stock_analysis=stock_analysis,
            recommendation=recommendation_data["action"],
            confidence=recommendation_data["confidence"],
            reasoning=recommendation_data["reasoning"],
            target_price=recommendation_data.get("target_price"),
            stop_loss=recommendation_data["stop_loss"],
            take_profit=recommendation_data["take_profit"]
        )

# 전역 포트폴리오 분석기 인스턴스
portfolio_analyzer = PortfolioAnalyzer()



