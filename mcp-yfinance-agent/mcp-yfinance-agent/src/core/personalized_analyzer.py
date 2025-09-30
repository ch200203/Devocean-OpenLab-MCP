from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from investment_profile import InvestmentProfile, RiskTolerance, InvestmentHorizon, TradingStyle
from memory_manager import memory_manager

@dataclass
class TechnicalIndicators:
    """기술적 지표"""
    sma_20: float
    sma_50: float
    rsi_14: float
    bollinger_upper: float
    bollinger_lower: float
    bollinger_middle: float
    volume_avg: float
    current_volume: float
    price_change_1d: float
    price_change_5d: float
    price_change_1m: float

@dataclass
class RiskEventAnalysis:
    """리스크 이벤트 분석 결과"""
    risk_score: int  # 0-100
    risk_level: str  # "low", "medium", "high", "critical"
    risk_factors: List[str]
    recent_events_count: int
    high_risk_events_count: int
    recommendation: str

@dataclass
class StockAnalysis:
    """종목 분석 결과"""
    ticker: str
    current_price: float
    currency: str
    exchange: str
    technical_indicators: TechnicalIndicators
    risk_score: float  # 0-100 (낮을수록 안전)
    volatility_score: float  # 0-100 (낮을수록 안정)
    momentum_score: float  # 0-100 (높을수록 상승 모멘텀)
    trend_score: float  # 0-100 (높을수록 상승 추세)
    volume_score: float  # 0-100 (높을수록 거래량 증가)
    overall_score: float  # 0-100 (종합 점수)
    risk_event_analysis: Optional[RiskEventAnalysis]  # 리스크 이벤트 분석 추가
    analysis_summary: str
    personalized_recommendation: str

class PersonalizedStockAnalyzer:
    """투자 성향 기반 맞춤형 종목 분석기"""
    
    def __init__(self):
        self.risk_weights = {
            RiskTolerance.CONSERVATIVE: {
                'risk_score': 0.4,
                'volatility_score': 0.3,
                'momentum_score': 0.2,
                'trend_score': 0.1
            },
            RiskTolerance.MODERATE: {
                'risk_score': 0.25,
                'volatility_score': 0.25,
                'momentum_score': 0.25,
                'trend_score': 0.25
            },
            RiskTolerance.AGGRESSIVE: {
                'risk_score': 0.1,
                'volatility_score': 0.2,
                'momentum_score': 0.35,
                'trend_score': 0.35
            }
        }
    
    def analyze_stock(self, ticker: str, user_id: str) -> Optional[StockAnalysis]:
        """종목 분석"""
        try:
            # 주식 데이터 가져오기
            stock_data = self._get_stock_data(ticker)
            if stock_data is None:
                return None
            
            # 기술적 지표 계산
            indicators = self._calculate_technical_indicators(stock_data)
            
            # 점수 계산
            scores = self._calculate_scores(indicators, stock_data)
            
            # 사용자 프로필 가져오기
            profile = memory_manager.get_user_profile(user_id)
            
            # 리스크 이벤트 분석 (MCP 에이전트를 통해)
            risk_event_analysis = self._analyze_risk_events(ticker)
            
            # 맞춤형 분석
            analysis_summary = self._generate_analysis_summary(indicators, scores, profile, risk_event_analysis)
            personalized_recommendation = self._generate_personalized_recommendation(
                ticker, indicators, scores, profile, risk_event_analysis
            )
            
            return StockAnalysis(
                ticker=ticker,
                current_price=stock_data['current_price'],
                currency=stock_data['currency'],
                exchange=stock_data['exchange'],
                technical_indicators=indicators,
                risk_score=scores['risk_score'],
                volatility_score=scores['volatility_score'],
                momentum_score=scores['momentum_score'],
                trend_score=scores['trend_score'],
                volume_score=scores['volume_score'],
                overall_score=scores['overall_score'],
                risk_event_analysis=risk_event_analysis,
                analysis_summary=analysis_summary,
                personalized_recommendation=personalized_recommendation
            )
            
        except Exception as e:
            print(f"종목 분석 중 오류 발생: {e}")
            return None
    
    def _get_stock_data(self, ticker: str) -> Optional[Dict]:
        """주식 데이터 가져오기"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="3mo")
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            currency = info.get('currency', 'USD')
            exchange = info.get('exchange', 'Unknown')
            
            return {
                'current_price': current_price,
                'currency': currency,
                'exchange': exchange,
                'history': hist
            }
        except Exception as e:
            print(f"주식 데이터 가져오기 실패: {e}")
            return None
    
    def _analyze_risk_events(self, ticker: str) -> Optional[RiskEventAnalysis]:
        """리스크 이벤트 분석 (MCP 에이전트 호출)"""
        try:
            # MCP 에이전트를 통한 리스크 분석
            # 실제 구현에서는 agent_graph의 investment_agent를 통해 호출
            # 여기서는 시뮬레이션 데이터 반환 (실제 MCP 호출은 agent_graph에서 처리)
            
            # 시뮬레이션: 실제로는 MCP 에이전트 호출
            # TODO: 실제 MCP 에이전트 호출로 대체 필요
            risk_score = 45  # 시뮬레이션 값
            risk_level = "medium"
            risk_factors = ["시장 변동성 증가", "재무 건전성 우려"]
            recent_events_count = 3
            high_risk_events_count = 1
            recommendation = "보통 수준의 리스크입니다. 적절한 리스크 관리가 필요합니다."
            
            return RiskEventAnalysis(
                risk_score=risk_score,
                risk_level=risk_level,
                risk_factors=risk_factors,
                recent_events_count=recent_events_count,
                high_risk_events_count=high_risk_events_count,
                recommendation=recommendation
            )
            
        except Exception as e:
            print(f"리스크 이벤트 분석 실패: {e}")
            return None
    
    def _calculate_technical_indicators(self, stock_data: Dict) -> TechnicalIndicators:
        """기술적 지표 계산"""
        hist = stock_data['history']
        current_price = stock_data['current_price']
        
        # 이동평균
        sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        
        # RSI 계산
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi_14 = 100 - (100 / (1 + rs.iloc[-1]))
        
        # 볼린저 밴드
        bb_period = 20
        bb_std = 2
        bb_middle = hist['Close'].rolling(window=bb_period).mean().iloc[-1]
        bb_std_val = hist['Close'].rolling(window=bb_period).std().iloc[-1]
        bollinger_upper = bb_middle + (bb_std_val * bb_std)
        bollinger_lower = bb_middle - (bb_std_val * bb_std)
        
        # 거래량
        volume_avg = hist['Volume'].rolling(window=20).mean().iloc[-1]
        current_volume = hist['Volume'].iloc[-1]
        
        # 가격 변화율
        price_change_1d = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
        price_change_5d = ((current_price - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100
        price_change_1m = ((current_price - hist['Close'].iloc[-22]) / hist['Close'].iloc[-22]) * 100
        
        return TechnicalIndicators(
            sma_20=sma_20,
            sma_50=sma_50,
            rsi_14=rsi_14,
            bollinger_upper=bollinger_upper,
            bollinger_lower=bollinger_lower,
            bollinger_middle=bb_middle,
            volume_avg=volume_avg,
            current_volume=current_volume,
            price_change_1d=price_change_1d,
            price_change_5d=price_change_5d,
            price_change_1m=price_change_1m
        )
    
    def _calculate_scores(self, indicators: TechnicalIndicators, stock_data: Dict) -> Dict[str, float]:
        """점수 계산"""
        # 리스크 점수 (낮을수록 안전)
        volatility = abs(indicators.price_change_1d) + abs(indicators.price_change_5d) / 5
        risk_score = min(100, volatility * 10)
        
        # 변동성 점수 (낮을수록 안정)
        volatility_score = min(100, volatility * 8)
        
        # 모멘텀 점수 (높을수록 상승 모멘텀)
        momentum_score = 50
        if indicators.rsi_14 > 50:
            momentum_score += (indicators.rsi_14 - 50) * 0.5
        else:
            momentum_score -= (50 - indicators.rsi_14) * 0.5
        
        # 추세 점수 (높을수록 상승 추세)
        trend_score = 50
        if indicators.sma_20 > indicators.sma_50:
            trend_score += 25
        if indicators.current_price > indicators.sma_20:
            trend_score += 25
        
        # 거래량 점수 (높을수록 거래량 증가)
        volume_ratio = indicators.current_volume / indicators.volume_avg
        volume_score = min(100, volume_ratio * 50)
        
        # 종합 점수
        overall_score = (risk_score * 0.2 + volatility_score * 0.2 + 
                        momentum_score * 0.3 + trend_score * 0.2 + volume_score * 0.1)
        
        return {
            'risk_score': risk_score,
            'volatility_score': volatility_score,
            'momentum_score': momentum_score,
            'trend_score': trend_score,
            'volume_score': volume_score,
            'overall_score': overall_score
        }
    
    def _generate_analysis_summary(self, indicators: TechnicalIndicators, 
                                 scores: Dict[str, float], profile: Optional[InvestmentProfile],
                                 risk_event_analysis: Optional[RiskEventAnalysis]) -> str:
        """분석 요약 생성"""
        summary_parts = []
        
        # 현재가 정보
        summary_parts.append(f"현재가: ${indicators.current_price:.2f}")
        
        # 기술적 지표 요약
        if indicators.sma_20 > indicators.sma_50:
            summary_parts.append("단기 이동평균이 장기 이동평균 위에 있어 상승 추세입니다.")
        else:
            summary_parts.append("단기 이동평균이 장기 이동평균 아래에 있어 하락 추세입니다.")
        
        # RSI 해석
        if indicators.rsi_14 > 70:
            summary_parts.append("RSI가 70 이상으로 과매수 상태입니다.")
        elif indicators.rsi_14 < 30:
            summary_parts.append("RSI가 30 이하로 과매도 상태입니다.")
        else:
            summary_parts.append("RSI가 중립 구간에 있습니다.")
        
        # 볼린저 밴드
        if indicators.current_price > indicators.bollinger_upper:
            summary_parts.append("볼린저 밴드 상단을 돌파했습니다.")
        elif indicators.current_price < indicators.bollinger_lower:
            summary_parts.append("볼린저 밴드 하단을 이탈했습니다.")
        
        # 거래량
        if indicators.current_volume > indicators.volume_avg * 1.5:
            summary_parts.append("거래량이 평균 대비 크게 증가했습니다.")
        
        # 리스크 이벤트 분석 추가
        if risk_event_analysis:
            summary_parts.append(f"리스크 레벨: {risk_event_analysis.risk_level} ({risk_event_analysis.risk_score}/100)")
            if risk_event_analysis.high_risk_events_count > 0:
                summary_parts.append(f"고위험 이벤트 {risk_event_analysis.high_risk_events_count}개 발생")
        
        return " | ".join(summary_parts)
    
    def _generate_personalized_recommendation(self, ticker: str, indicators: TechnicalIndicators,
                                            scores: Dict[str, float], 
                                            profile: Optional[InvestmentProfile],
                                            risk_event_analysis: Optional[RiskEventAnalysis]) -> str:
        """맞춤형 추천 생성"""
        if not profile:
            return "투자 성향 프로필이 없어 일반적인 분석만 제공됩니다."
        
        recommendations = []
        
        # 투자 성향별 가중치 적용
        weights = self.risk_weights.get(profile.risk_tolerance, self.risk_weights[RiskTolerance.MODERATE])
        weighted_score = (
            scores['risk_score'] * weights['risk_score'] +
            scores['volatility_score'] * weights['volatility_score'] +
            scores['momentum_score'] * weights['momentum_score'] +
            scores['trend_score'] * weights['trend_score']
        )
        
        # 투자 성향별 추천
        if profile.risk_tolerance == RiskTolerance.CONSERVATIVE:
            if weighted_score < 30:
                recommendations.append("보수적 투자자에게 적합한 안정적인 종목입니다.")
            elif weighted_score > 70:
                recommendations.append("변동성이 높아 보수적 투자자에게는 위험할 수 있습니다.")
            else:
                recommendations.append("보수적 투자자에게 적당한 수준의 종목입니다.")
        
        elif profile.risk_tolerance == RiskTolerance.MODERATE:
            if weighted_score < 40:
                recommendations.append("중간 성향 투자자에게 안정적인 선택입니다.")
            elif weighted_score > 60:
                recommendations.append("중간 성향 투자자에게 적당한 위험 수준입니다.")
            else:
                recommendations.append("중간 성향 투자자에게 균형잡힌 종목입니다.")
        
        else:  # AGGRESSIVE
            if weighted_score < 50:
                recommendations.append("공격적 투자자에게는 수익 기회가 제한적일 수 있습니다.")
            else:
                recommendations.append("공격적 투자자에게 적합한 고수익 기회 종목입니다.")
        
        # 거래 스타일별 추천
        if profile.trading_style == TradingStyle.DAY_TRADING:
            if abs(indicators.price_change_1d) > 3:
                recommendations.append("당일 거래에 적합한 변동성을 보입니다.")
        
        elif profile.trading_style == TradingStyle.SWING_TRADING:
            if abs(indicators.price_change_5d) > 5:
                recommendations.append("스윙 거래에 적합한 단기 추세를 보입니다.")
        
        elif profile.trading_style == TradingStyle.POSITION_TRADING:
            if abs(indicators.price_change_1m) > 10:
                recommendations.append("포지션 거래에 적합한 중장기 추세를 보입니다.")
        
        # 손절/익절 가이드라인
        recommendations.append(f"권장 손절매: -{profile.stop_loss_tolerance}%")
        recommendations.append(f"권장 익절매: +{profile.take_profit_target}%")
        
        # 리스크 이벤트 기반 추천 추가
        if risk_event_analysis:
            recommendations.append(f"리스크 이벤트 분석: {risk_event_analysis.recommendation}")
            if risk_event_analysis.risk_level in ["high", "critical"]:
                recommendations.append("고위험 상태로 투자 신중 검토 필요")
        
        return " | ".join(recommendations)

class BuySellRecommendationEngine:
    """매수/매도 추천 엔진"""
    
    def __init__(self):
        self.analyzer = PersonalizedStockAnalyzer()
    
    def get_recommendation(self, ticker: str, user_id: str) -> Dict[str, Any]:
        """매수/매도 추천"""
        analysis = self.analyzer.analyze_stock(ticker, user_id)
        if not analysis:
            return {"error": "종목 분석에 실패했습니다."}
        
        profile = memory_manager.get_user_profile(user_id)
        if not profile:
            return {"error": "투자 성향 프로필이 없습니다."}
        
        # 추천 로직
        recommendation = self._calculate_recommendation(analysis, profile)
        
        return {
            "ticker": ticker,
            "current_price": analysis.current_price,
            "currency": analysis.currency,
            "recommendation": recommendation["action"],
            "confidence": recommendation["confidence"],
            "reasoning": recommendation["reasoning"],
            "buy_price_range": recommendation["buy_price_range"],
            "sell_price_range": recommendation["sell_price_range"],
            "stop_loss": recommendation["stop_loss"],
            "take_profit": recommendation["take_profit"],
            "time_horizon": recommendation["time_horizon"],
            "risk_level": recommendation["risk_level"],
            "risk_event_analysis": analysis.risk_event_analysis
        }
    
    def _calculate_recommendation(self, analysis: StockAnalysis, 
                                profile: InvestmentProfile) -> Dict[str, Any]:
        """추천 계산"""
        current_price = analysis.current_price
        indicators = analysis.technical_indicators
        
        # 기본 점수 계산
        buy_score = 0
        sell_score = 0
        
        # 기술적 지표 기반 점수
        if indicators.sma_20 > indicators.sma_50:
            buy_score += 20
        else:
            sell_score += 20
        
        if indicators.rsi_14 < 30:
            buy_score += 25  # 과매도
        elif indicators.rsi_14 > 70:
            sell_score += 25  # 과매수
        
        if indicators.current_price < indicators.bollinger_lower:
            buy_score += 15
        elif indicators.current_price > indicators.bollinger_upper:
            sell_score += 15
        
        if indicators.current_volume > indicators.volume_avg * 1.5:
            if indicators.price_change_1d > 0:
                buy_score += 10
            else:
                sell_score += 10
        
        # 투자 성향별 가중치 적용
        if profile.risk_tolerance == RiskTolerance.CONSERVATIVE:
            if analysis.risk_score > 60:
                sell_score += 20
        elif profile.risk_tolerance == RiskTolerance.AGGRESSIVE:
            if analysis.momentum_score > 70:
                buy_score += 15
        
        # 리스크 이벤트 분석 고려
        if analysis.risk_event_analysis:
            if analysis.risk_event_analysis.risk_level == "critical":
                sell_score += 30
            elif analysis.risk_event_analysis.risk_level == "high":
                sell_score += 15
            elif analysis.risk_event_analysis.risk_level == "low":
                buy_score += 10
        
        # 최종 추천 결정
        if buy_score > sell_score + 10:
            action = "BUY"
            confidence = min(95, buy_score)
        elif sell_score > buy_score + 10:
            action = "SELL"
            confidence = min(95, sell_score)
        else:
            action = "HOLD"
            confidence = 50
        
        # 가격 범위 계산
        buy_price_range = self._calculate_buy_price_range(current_price, profile)
        sell_price_range = self._calculate_sell_price_range(current_price, profile)
        
        # 추천 이유 생성
        reasoning = self._generate_reasoning(analysis, profile, action)
        
        return {
            "action": action,
            "confidence": confidence,
            "reasoning": reasoning,
            "buy_price_range": buy_price_range,
            "sell_price_range": sell_price_range,
            "stop_loss": current_price * (1 - profile.stop_loss_tolerance / 100),
            "take_profit": current_price * (1 + profile.take_profit_target / 100),
            "time_horizon": profile.investment_horizon.value,
            "risk_level": profile.risk_tolerance.value
        }
    
    def _calculate_buy_price_range(self, current_price: float, 
                                 profile: InvestmentProfile) -> Dict[str, float]:
        """매수 가격 범위 계산"""
        if profile.risk_tolerance == RiskTolerance.CONSERVATIVE:
            # 보수적: 현재가보다 낮은 가격에서 매수
            lower = current_price * 0.95
            upper = current_price * 0.98
        elif profile.risk_tolerance == RiskTolerance.AGGRESSIVE:
            # 공격적: 현재가 근처에서도 매수 가능
            lower = current_price * 0.97
            upper = current_price * 1.02
        else:  # MODERATE
            lower = current_price * 0.96
            upper = current_price * 1.00
        
        return {"lower": lower, "upper": upper}
    
    def _calculate_sell_price_range(self, current_price: float, 
                                  profile: InvestmentProfile) -> Dict[str, float]:
        """매도 가격 범위 계산"""
        if profile.risk_tolerance == RiskTolerance.CONSERVATIVE:
            # 보수적: 빠른 익절
            lower = current_price * 1.02
            upper = current_price * 1.08
        elif profile.risk_tolerance == RiskTolerance.AGGRESSIVE:
            # 공격적: 높은 수익 목표
            lower = current_price * 1.05
            upper = current_price * 1.20
        else:  # MODERATE
            lower = current_price * 1.03
            upper = current_price * 1.12
        
        return {"lower": lower, "upper": upper}
    
    def _generate_reasoning(self, analysis: StockAnalysis, 
                          profile: InvestmentProfile, action: str) -> str:
        """추천 이유 생성"""
        reasons = []
        
        if action == "BUY":
            reasons.append("기술적 지표가 매수 신호를 보이고 있습니다.")
            if analysis.momentum_score > 60:
                reasons.append("상승 모멘텀이 강합니다.")
            if analysis.trend_score > 60:
                reasons.append("상승 추세가 지속되고 있습니다.")
        elif action == "SELL":
            reasons.append("기술적 지표가 매도 신호를 보이고 있습니다.")
            if analysis.risk_score > 70:
                reasons.append("변동성이 높아 위험합니다.")
            if analysis.momentum_score < 40:
                reasons.append("하락 모멘텀이 감지됩니다.")
        else:  # HOLD
            reasons.append("현재 상황을 지켜보는 것이 좋겠습니다.")
            reasons.append("명확한 방향성이 나타날 때까지 대기하세요.")
        
        # 투자 성향별 추가 이유
        if profile.risk_tolerance == RiskTolerance.CONSERVATIVE:
            reasons.append("보수적 투자자에게 적합한 리스크 관리가 필요합니다.")
        elif profile.risk_tolerance == RiskTolerance.AGGRESSIVE:
            reasons.append("공격적 투자자에게 적합한 수익 기회입니다.")
        
        # 리스크 이벤트 기반 이유 추가
        if analysis.risk_event_analysis:
            if analysis.risk_event_analysis.risk_level == "critical":
                reasons.append("중대한 리스크 이벤트가 발생하여 신중한 접근이 필요합니다.")
            elif analysis.risk_event_analysis.risk_level == "high":
                reasons.append("높은 리스크 이벤트가 감지되어 주의가 필요합니다.")
            elif analysis.risk_event_analysis.risk_level == "low":
                reasons.append("리스크 이벤트가 적어 상대적으로 안전한 환경입니다.")
        
        return " | ".join(reasons)

