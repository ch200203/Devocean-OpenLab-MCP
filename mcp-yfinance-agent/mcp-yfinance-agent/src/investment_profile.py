from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Literal
from enum import Enum
import json
import os
from datetime import datetime

class RiskTolerance(Enum):
    CONSERVATIVE = "conservative"  # 보수적
    MODERATE = "moderate"         # 중간
    AGGRESSIVE = "aggressive"     # 공격적

class InvestmentHorizon(Enum):
    SHORT_TERM = "short_term"     # 단기 (1개월 이하)
    MEDIUM_TERM = "medium_term"   # 중기 (1-6개월)
    LONG_TERM = "long_term"       # 장기 (6개월 이상)

class TradingStyle(Enum):
    DAY_TRADING = "day_trading"       # 당일 거래
    SWING_TRADING = "swing_trading"   # 스윙 거래
    POSITION_TRADING = "position_trading"  # 포지션 거래
    VALUE_INVESTING = "value_investing"    # 가치 투자

@dataclass
class InvestmentProfile:
    """투자 성향 프로필"""
    user_id: str
    risk_tolerance: RiskTolerance
    investment_horizon: InvestmentHorizon
    trading_style: TradingStyle
    preferred_sectors: List[str]  # 선호 섹터
    max_position_size: float      # 최대 포지션 크기 (%)
    stop_loss_tolerance: float    # 손절매 허용 범위 (%)
    take_profit_target: float     # 익절 목표 (%)
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['risk_tolerance'] = self.risk_tolerance.value
        data['investment_horizon'] = self.investment_horizon.value
        data['trading_style'] = self.trading_style.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'InvestmentProfile':
        """딕셔너리에서 생성"""
        data['risk_tolerance'] = RiskTolerance(data['risk_tolerance'])
        data['investment_horizon'] = InvestmentHorizon(data['investment_horizon'])
        data['trading_style'] = TradingStyle(data['trading_style'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)

class InvestmentProfileManager:
    """투자 성향 프로필 관리자"""
    
    def __init__(self, storage_path: str = "investment_profiles.json"):
        self.storage_path = storage_path
        self.profiles: Dict[str, InvestmentProfile] = {}
        self.load_profiles()
    
    def load_profiles(self):
        """프로필 파일에서 로드"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_id, profile_data in data.items():
                        self.profiles[user_id] = InvestmentProfile.from_dict(profile_data)
            except Exception as e:
                print(f"프로필 로드 실패: {e}")
    
    def save_profiles(self):
        """프로필을 파일에 저장"""
        try:
            data = {user_id: profile.to_dict() for user_id, profile in self.profiles.items()}
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"프로필 저장 실패: {e}")
    
    def get_profile(self, user_id: str) -> Optional[InvestmentProfile]:
        """사용자 프로필 조회"""
        return self.profiles.get(user_id)
    
    def save_profile(self, profile: InvestmentProfile):
        """프로필 저장"""
        self.profiles[profile.user_id] = profile
        self.save_profiles()
    
    def update_profile(self, user_id: str, **kwargs):
        """프로필 업데이트"""
        if user_id in self.profiles:
            profile = self.profiles[user_id]
            for key, value in kwargs.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            profile.updated_at = datetime.now()
            self.save_profiles()
    
    def delete_profile(self, user_id: str):
        """프로필 삭제"""
        if user_id in self.profiles:
            del self.profiles[user_id]
            self.save_profiles()

class InvestmentProfileBuilder:
    """투자 성향 프로필 빌더"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.risk_tolerance: Optional[RiskTolerance] = None
        self.investment_horizon: Optional[InvestmentHorizon] = None
        self.trading_style: Optional[TradingStyle] = None
        self.preferred_sectors: List[str] = []
        self.max_position_size: Optional[float] = None
        self.stop_loss_tolerance: Optional[float] = None
        self.take_profit_target: Optional[float] = None
    
    def set_risk_tolerance(self, risk_tolerance: RiskTolerance):
        self.risk_tolerance = risk_tolerance
        return self
    
    def set_investment_horizon(self, horizon: InvestmentHorizon):
        self.investment_horizon = horizon
        return self
    
    def set_trading_style(self, style: TradingStyle):
        self.trading_style = style
        return self
    
    def add_preferred_sector(self, sector: str):
        if sector not in self.preferred_sectors:
            self.preferred_sectors.append(sector)
        return self
    
    def set_position_limits(self, max_position: float, stop_loss: float, take_profit: float):
        self.max_position_size = max_position
        self.stop_loss_tolerance = stop_loss
        self.take_profit_target = take_profit
        return self
    
    def build(self) -> InvestmentProfile:
        """프로필 생성"""
        if not all([self.risk_tolerance, self.investment_horizon, self.trading_style]):
            raise ValueError("필수 투자 성향 정보가 누락되었습니다.")
        
        # 기본값 설정
        if not self.max_position_size:
            self.max_position_size = self._get_default_position_size()
        if not self.stop_loss_tolerance:
            self.stop_loss_tolerance = self._get_default_stop_loss()
        if not self.take_profit_target:
            self.take_profit_target = self._get_default_take_profit()
        
        now = datetime.now()
        return InvestmentProfile(
            user_id=self.user_id,
            risk_tolerance=self.risk_tolerance,
            investment_horizon=self.investment_horizon,
            trading_style=self.trading_style,
            preferred_sectors=self.preferred_sectors,
            max_position_size=self.max_position_size,
            stop_loss_tolerance=self.stop_loss_tolerance,
            take_profit_target=self.take_profit_target,
            created_at=now,
            updated_at=now
        )
    
    def _get_default_position_size(self) -> float:
        """리스크 성향에 따른 기본 포지션 크기"""
        if self.risk_tolerance == RiskTolerance.CONSERVATIVE:
            return 5.0
        elif self.risk_tolerance == RiskTolerance.MODERATE:
            return 10.0
        else:  # AGGRESSIVE
            return 20.0
    
    def _get_default_stop_loss(self) -> float:
        """리스크 성향에 따른 기본 손절매 범위"""
        if self.risk_tolerance == RiskTolerance.CONSERVATIVE:
            return 3.0
        elif self.risk_tolerance == RiskTolerance.MODERATE:
            return 5.0
        else:  # AGGRESSIVE
            return 8.0
    
    def _get_default_take_profit(self) -> float:
        """리스크 성향에 따른 기본 익절 목표"""
        if self.risk_tolerance == RiskTolerance.CONSERVATIVE:
            return 6.0
        elif self.risk_tolerance == RiskTolerance.MODERATE:
            return 10.0
        else:  # AGGRESSIVE
            return 15.0

# 투자 성향 설문 질문들
INVESTMENT_QUESTIONNAIRE = {
    "risk_tolerance": {
        "question": "다음 중 어떤 투자 성향이 가장 적합한가요?",
        "options": {
            "conservative": "보수적 - 안정적인 수익을 원하며 손실을 최소화하고 싶습니다",
            "moderate": "중간 - 적당한 위험을 감수하며 균형잡힌 수익을 원합니다",
            "aggressive": "공격적 - 높은 수익을 위해 높은 위험도 감수할 수 있습니다"
        }
    },
    "investment_horizon": {
        "question": "투자 기간은 얼마나 계획하고 계신가요?",
        "options": {
            "short_term": "단기 (1개월 이하) - 빠른 수익을 원합니다",
            "medium_term": "중기 (1-6개월) - 적당한 기간의 투자를 원합니다",
            "long_term": "장기 (6개월 이상) - 장기적인 관점에서 투자합니다"
        }
    },
    "trading_style": {
        "question": "어떤 거래 스타일을 선호하시나요?",
        "options": {
            "day_trading": "당일 거래 - 하루 안에 매매를 완료합니다",
            "swing_trading": "스윙 거래 - 며칠에서 몇 주 단위로 거래합니다",
            "position_trading": "포지션 거래 - 몇 주에서 몇 개월 단위로 거래합니다",
            "value_investing": "가치 투자 - 기업의 내재가치를 분석하여 장기 투자합니다"
        }
    },
    "sectors": {
        "question": "관심 있는 섹터를 선택해주세요 (복수 선택 가능):",
        "options": {
            "technology": "기술/IT",
            "healthcare": "헬스케어/바이오",
            "finance": "금융",
            "energy": "에너지",
            "consumer": "소비재",
            "industrial": "산업재",
            "materials": "소재",
            "utilities": "유틸리티",
            "real_estate": "부동산",
            "communication": "통신"
        }
    }
}
