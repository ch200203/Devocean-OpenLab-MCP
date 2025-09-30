#!/usr/bin/env python3
"""
독립 실행 가능한 리스크 분석기
MCP 서버 없이 직접 실행
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class RiskEvent:
    """리스크 이벤트 정보"""
    event_type: str  # "financial", "legal", "market", "operational", "regulatory"
    severity: str    # "low", "medium", "high", "critical"
    title: str
    description: str
    source: str
    published_date: str
    confidence: float  # 0.0 - 1.0
    keywords: List[str]
    risk_score: int   # 0-100

@dataclass
class RiskAnalysis:
    """리스크 분석 결과"""
    ticker: str
    overall_risk_score: int  # 0-100
    risk_level: str  # "low", "medium", "high", "critical"
    total_events: int
    high_risk_events: int
    recent_events: List[RiskEvent]
    risk_factors: List[str]
    recommendation: str
    last_updated: str

class RiskEventDetector:
    """리스크 이벤트 감지기"""
    
    def __init__(self):
        self.risk_keywords = {
            "financial": [
                "손실", "적자", "매출 감소", "이익 감소", "부채 증가", "현금 부족",
                "loss", "deficit", "revenue decline", "profit decrease", "debt increase"
            ],
            "legal": [
                "소송", "법적 분쟁", "규제 위반", "벌금", "제재",
                "lawsuit", "legal dispute", "regulatory violation", "fine", "sanction"
            ],
            "market": [
                "주가 하락", "거래 중단", "유동성 부족", "시장 충격",
                "stock decline", "trading halt", "liquidity shortage", "market shock"
            ],
            "operational": [
                "공장 폐쇄", "생산 중단", "공급망 문제", "품질 문제", "사고",
                "factory closure", "production halt", "supply chain", "quality issue", "accident"
            ],
            "regulatory": [
                "규제 강화", "허가 취소", "정부 조사", "정책 변경",
                "regulatory tightening", "license revocation", "government investigation", "policy change"
            ]
        }
        
        self.severity_keywords = {
            "critical": ["폐업", "파산", "상장폐지", "bankruptcy", "delisting", "closure"],
            "high": ["중대", "심각", "긴급", "serious", "severe", "urgent"],
            "medium": ["주의", "관심", "caution", "concern"],
            "low": ["소폭", "일시적", "minor", "temporary"]
        }
    
    def analyze_ticker_risk(self, ticker: str) -> RiskAnalysis:
        """종목 리스크 분석"""
        try:
            # 1. 뉴스 데이터 수집
            news_events = self._collect_news_events(ticker)
            
            # 2. 공시 데이터 수집 (DART API 대신 시뮬레이션)
            disclosure_events = self._collect_disclosure_events(ticker)
            
            # 3. 소셜 미디어 데이터 수집 (시뮬레이션)
            social_events = self._collect_social_events(ticker)
            
            # 4. 모든 이벤트 통합
            all_events = news_events + disclosure_events + social_events
            
            # 5. 리스크 점수 계산
            risk_score = self._calculate_risk_score(all_events)
            
            # 6. 리스크 레벨 결정
            risk_level = self._determine_risk_level(risk_score)
            
            # 7. 리스크 팩터 추출
            risk_factors = self._extract_risk_factors(all_events)
            
            # 8. 추천 생성
            recommendation = self._generate_recommendation(risk_score, risk_level, all_events)
            
            return RiskAnalysis(
                ticker=ticker,
                overall_risk_score=risk_score,
                risk_level=risk_level,
                total_events=len(all_events),
                high_risk_events=len([e for e in all_events if e.risk_score >= 70]),
                recent_events=all_events[:5],  # 최근 5개 이벤트
                risk_factors=risk_factors,
                recommendation=recommendation,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"리스크 분석 중 오류: {e}")
            return self._create_default_analysis(ticker)
    
    def _collect_news_events(self, ticker: str) -> List[RiskEvent]:
        """뉴스 이벤트 수집 (시뮬레이션)"""
        simulated_news = [
            {
                "title": f"{ticker} 실적 발표, 예상보다 낮은 매출",
                "content": f"{ticker}의 분기 실적이 분석가 예상을 하회하며 주가 하락 우려",
                "source": "Financial News",
                "date": (datetime.now() - timedelta(days=2)).isoformat(),
                "keywords": ["실적", "매출 감소", "주가 하락"]
            },
            {
                "title": f"{ticker} 신제품 출시 지연",
                "content": f"{ticker}의 핵심 신제품 출시가 예정보다 3개월 지연될 예정",
                "source": "Tech News",
                "date": (datetime.now() - timedelta(days=5)).isoformat(),
                "keywords": ["출시 지연", "생산 문제"]
            }
        ]
        
        events = []
        for news in simulated_news:
            event_type, severity, confidence = self._classify_news_content(
                news["title"], news["content"], news["keywords"]
            )
            
            risk_score = self._calculate_event_risk_score(event_type, severity, confidence)
            
            events.append(RiskEvent(
                event_type=event_type,
                severity=severity,
                title=news["title"],
                description=news["content"],
                source=news["source"],
                published_date=news["date"],
                confidence=confidence,
                keywords=news["keywords"],
                risk_score=risk_score
            ))
        
        return events
    
    def _collect_disclosure_events(self, ticker: str) -> List[RiskEvent]:
        """공시 이벤트 수집 (시뮬레이션)"""
        simulated_disclosures = [
            {
                "title": f"{ticker} 주요 주주 지분 변동 공시",
                "content": f"{ticker}의 주요 주주가 보유 지분을 5% 감소시켰다고 공시",
                "source": "DART",
                "date": (datetime.now() - timedelta(days=1)).isoformat(),
                "keywords": ["주주", "지분 변동", "매도"]
            }
        ]
        
        events = []
        for disclosure in simulated_disclosures:
            event_type, severity, confidence = self._classify_news_content(
                disclosure["title"], disclosure["content"], disclosure["keywords"]
            )
            
            risk_score = self._calculate_event_risk_score(event_type, severity, confidence)
            
            events.append(RiskEvent(
                event_type=event_type,
                severity=severity,
                title=disclosure["title"],
                description=disclosure["content"],
                source=disclosure["source"],
                published_date=disclosure["date"],
                confidence=confidence,
                keywords=disclosure["keywords"],
                risk_score=risk_score
            ))
        
        return events
    
    def _collect_social_events(self, ticker: str) -> List[RiskEvent]:
        """소셜 미디어 이벤트 수집 (시뮬레이션)"""
        simulated_social = [
            {
                "title": f"{ticker} 관련 부정적 여론 확산",
                "content": f"소셜 미디어에서 {ticker} 관련 부정적 댓글이 급증하고 있음",
                "source": "Social Media Monitor",
                "date": (datetime.now() - timedelta(hours=6)).isoformat(),
                "keywords": ["부정적", "여론", "댓글"]
            }
        ]
        
        events = []
        for social in simulated_social:
            event_type, severity, confidence = self._classify_news_content(
                social["title"], social["content"], social["keywords"]
            )
            
            risk_score = self._calculate_event_risk_score(event_type, severity, confidence)
            
            events.append(RiskEvent(
                event_type=event_type,
                severity=severity,
                title=social["title"],
                description=social["content"],
                source=social["source"],
                published_date=social["date"],
                confidence=confidence,
                keywords=social["keywords"],
                risk_score=risk_score
            ))
        
        return events
    
    def _classify_news_content(self, title: str, content: str, keywords: List[str]) -> tuple:
        """뉴스 내용 분류"""
        text = f"{title} {content}".lower()
        
        # 이벤트 타입 분류
        event_type = "market"  # 기본값
        for event_type_key, type_keywords in self.risk_keywords.items():
            for keyword in type_keywords:
                if keyword.lower() in text:
                    event_type = event_type_key
                    break
            if event_type != "market":
                break
        
        # 심각도 분류
        severity = "medium"  # 기본값
        for severity_key, severity_keywords in self.severity_keywords.items():
            for keyword in severity_keywords:
                if keyword.lower() in text:
                    severity = severity_key
                    break
            if severity != "medium":
                break
        
        # 신뢰도 계산 (키워드 매칭 기반)
        confidence = 0.5
        matched_keywords = 0
        for keyword in keywords:
            if keyword.lower() in text:
                matched_keywords += 1
        
        if matched_keywords > 0:
            confidence = min(0.9, 0.5 + (matched_keywords * 0.1))
        
        return event_type, severity, confidence
    
    def _calculate_event_risk_score(self, event_type: str, severity: str, confidence: float) -> int:
        """개별 이벤트 리스크 점수 계산"""
        # 이벤트 타입별 기본 점수
        type_scores = {
            "financial": 70,
            "legal": 80,
            "market": 60,
            "operational": 65,
            "regulatory": 75
        }
        
        # 심각도별 가중치
        severity_weights = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
        
        base_score = type_scores.get(event_type, 60)
        weight = severity_weights.get(severity, 0.6)
        
        # 최종 점수 = 기본점수 * 심각도가중치 * 신뢰도
        final_score = int(base_score * weight * confidence)
        
        return min(100, max(0, final_score))
    
    def _calculate_risk_score(self, events: List[RiskEvent]) -> int:
        """전체 리스크 점수 계산"""
        if not events:
            return 20  # 기본 리스크
        
        # 가중 평균 계산 (최근 이벤트에 더 높은 가중치)
        weighted_sum = 0
        total_weight = 0
        
        for i, event in enumerate(events):
            # 최근 이벤트일수록 높은 가중치 (지수 감소)
            weight = 1.0 / (i + 1)
            weighted_sum += event.risk_score * weight
            total_weight += weight
        
        if total_weight > 0:
            avg_score = weighted_sum / total_weight
        else:
            avg_score = 50
        
        # 높은 리스크 이벤트가 많으면 보너스 점수
        high_risk_count = len([e for e in events if e.risk_score >= 70])
        if high_risk_count > 0:
            avg_score += min(20, high_risk_count * 5)
        
        return min(100, int(avg_score))
    
    def _determine_risk_level(self, risk_score: int) -> str:
        """리스크 레벨 결정"""
        if risk_score >= 80:
            return "critical"
        elif risk_score >= 60:
            return "high"
        elif risk_score >= 40:
            return "medium"
        else:
            return "low"
    
    def _extract_risk_factors(self, events: List[RiskEvent]) -> List[str]:
        """리스크 팩터 추출"""
        factors = []
        event_types = set()
        
        for event in events:
            event_types.add(event.event_type)
        
        # 이벤트 타입별 리스크 팩터 설명
        factor_descriptions = {
            "financial": "재무 건전성 우려",
            "legal": "법적 리스크 존재",
            "market": "시장 변동성 증가",
            "operational": "운영상 문제 발생",
            "regulatory": "규제 리스크 증가"
        }
        
        for event_type in event_types:
            if event_type in factor_descriptions:
                factors.append(factor_descriptions[event_type])
        
        return factors
    
    def _generate_recommendation(self, risk_score: int, risk_level: str, events: List[RiskEvent]) -> str:
        """추천 생성"""
        if risk_level == "critical":
            return "매우 높은 리스크 상태입니다. 투자 재검토가 필요합니다."
        elif risk_level == "high":
            return "높은 리스크 상태입니다. 신중한 접근이 필요합니다."
        elif risk_level == "medium":
            return "보통 수준의 리스크입니다. 적절한 리스크 관리가 필요합니다."
        else:
            return "낮은 리스크 상태입니다. 상대적으로 안전한 투자 환경입니다."
    
    def _create_default_analysis(self, ticker: str) -> RiskAnalysis:
        """기본 분석 결과 생성"""
        return RiskAnalysis(
            ticker=ticker,
            overall_risk_score=30,
            risk_level="low",
            total_events=0,
            high_risk_events=0,
            recent_events=[],
            risk_factors=["데이터 수집 실패"],
            recommendation="리스크 분석을 위한 데이터를 수집할 수 없습니다.",
            last_updated=datetime.now().isoformat()
        )

def main():
    """메인 함수"""
    print("🚀 AAPL 리스크 에이전트 실행")
    print("=" * 50)
    
    # 리스크 감지기 생성
    detector = RiskEventDetector()
    
    # AAPL 리스크 분석 실행
    print(f"\n📊 AAPL 리스크 분석 시작...")
    analysis = detector.analyze_ticker_risk("AAPL")
    
    # 결과 출력
    print(f"\n📈 AAPL 리스크 분석 결과")
    print("-" * 30)
    print(f"종목: {analysis.ticker}")
    print(f"전체 리스크 점수: {analysis.overall_risk_score}/100")
    print(f"리스크 레벨: {analysis.risk_level.upper()}")
    print(f"총 이벤트 수: {analysis.total_events}")
    print(f"고위험 이벤트: {analysis.high_risk_events}")
    print(f"추천: {analysis.recommendation}")
    
    if analysis.risk_factors:
        print(f"\n⚠️  리스크 팩터:")
        for i, factor in enumerate(analysis.risk_factors, 1):
            print(f"  {i}. {factor}")
    
    print(f"\n📰 최근 이벤트 ({len(analysis.recent_events)}개):")
    for i, event in enumerate(analysis.recent_events, 1):
        print(f"\n  {i}. {event.title}")
        print(f"     타입: {event.event_type}")
        print(f"     심각도: {event.severity}")
        print(f"     리스크 점수: {event.risk_score}/100")
        print(f"     출처: {event.source}")
        print(f"     날짜: {event.published_date}")
        print(f"     설명: {event.description}")
        print(f"     키워드: {', '.join(event.keywords)}")
    
    print(f"\n✅ 리스크 분석 완료!")
    print(f"마지막 업데이트: {analysis.last_updated}")

if __name__ == "__main__":
    main()
