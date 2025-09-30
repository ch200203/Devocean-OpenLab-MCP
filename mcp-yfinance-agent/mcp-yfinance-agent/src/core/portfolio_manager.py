from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
from investment_profile import InvestmentProfile

@dataclass
class Position:
    """보유 포지션"""
    ticker: str
    quantity: float  # 보유 수량
    average_price: float  # 평단가
    current_price: float = 0.0  # 현재가 (분석 시 업데이트)
    currency: str = "USD"
    sector: str = ""
    purchase_date: datetime = None
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.purchase_date is None:
            self.purchase_date = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    @property
    def market_value(self) -> float:
        """현재 시장 가치"""
        return self.quantity * self.current_price
    
    @property
    def cost_basis(self) -> float:
        """매수 원금"""
        return self.quantity * self.average_price
    
    @property
    def unrealized_pnl(self) -> float:
        """미실현 손익"""
        return self.market_value - self.cost_basis
    
    @property
    def unrealized_pnl_percent(self) -> float:
        """미실현 손익률 (%)"""
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 100
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['purchase_date'] = self.purchase_date.isoformat()
        data['last_updated'] = self.last_updated.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Position':
        """딕셔너리에서 생성"""
        data['purchase_date'] = datetime.fromisoformat(data['purchase_date'])
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)

@dataclass
class Portfolio:
    """포트폴리오"""
    user_id: str
    positions: Dict[str, Position]  # ticker -> Position
    total_invested: float = 0.0
    total_market_value: float = 0.0
    total_unrealized_pnl: float = 0.0
    total_unrealized_pnl_percent: float = 0.0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()
        self._calculate_totals()
    
    def _calculate_totals(self):
        """총계 계산"""
        self.total_invested = sum(pos.cost_basis for pos in self.positions.values())
        self.total_market_value = sum(pos.market_value for pos in self.positions.values())
        self.total_unrealized_pnl = self.total_market_value - self.total_invested
        if self.total_invested > 0:
            self.total_unrealized_pnl_percent = (self.total_unrealized_pnl / self.total_invested) * 100
        else:
            self.total_unrealized_pnl_percent = 0.0
    
    def add_position(self, ticker: str, quantity: float, average_price: float, 
                    currency: str = "USD", sector: str = "") -> Position:
        """포지션 추가"""
        if ticker in self.positions:
            # 기존 포지션과 평균 계산
            existing = self.positions[ticker]
            total_quantity = existing.quantity + quantity
            total_cost = existing.cost_basis + (quantity * average_price)
            new_average_price = total_cost / total_quantity
            
            position = Position(
                ticker=ticker,
                quantity=total_quantity,
                average_price=new_average_price,
                currency=currency,
                sector=sector,
                purchase_date=existing.purchase_date,
                last_updated=datetime.now()
            )
        else:
            position = Position(
                ticker=ticker,
                quantity=quantity,
                average_price=average_price,
                currency=currency,
                sector=sector,
                last_updated=datetime.now()
            )
        
        self.positions[ticker] = position
        self.last_updated = datetime.now()
        self._calculate_totals()
        return position
    
    def update_position(self, ticker: str, current_price: float) -> Optional[Position]:
        """포지션 현재가 업데이트"""
        if ticker in self.positions:
            position = self.positions[ticker]
            position.current_price = current_price
            position.last_updated = datetime.now()
            self.last_updated = datetime.now()
            self._calculate_totals()
            return position
        return None
    
    def remove_position(self, ticker: str) -> Optional[Position]:
        """포지션 제거"""
        if ticker in self.positions:
            position = self.positions.pop(ticker)
            self.last_updated = datetime.now()
            self._calculate_totals()
            return position
        return None
    
    def get_position(self, ticker: str) -> Optional[Position]:
        """포지션 조회"""
        return self.positions.get(ticker)
    
    def get_sector_allocation(self) -> Dict[str, float]:
        """섹터별 할당 비율"""
        sector_values = {}
        for position in self.positions.values():
            if position.sector:
                if position.sector not in sector_values:
                    sector_values[position.sector] = 0.0
                sector_values[position.sector] += position.market_value
        
        total_value = sum(sector_values.values())
        if total_value > 0:
            return {sector: (value / total_value) * 100 for sector, value in sector_values.items()}
        return {}
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['positions'] = {ticker: pos.to_dict() for ticker, pos in self.positions.items()}
        data['last_updated'] = self.last_updated.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Portfolio':
        """딕셔너리에서 생성"""
        positions = {}
        for ticker, pos_data in data['positions'].items():
            positions[ticker] = Position.from_dict(pos_data)
        data['positions'] = positions
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)

class PortfolioManager:
    """포트폴리오 관리자"""
    
    def __init__(self, storage_path: str = "portfolios.json"):
        self.storage_path = storage_path
        self.portfolios: Dict[str, Portfolio] = {}
        self.load_portfolios()
    
    def load_portfolios(self):
        """포트폴리오 파일에서 로드"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_id, portfolio_data in data.items():
                        self.portfolios[user_id] = Portfolio.from_dict(portfolio_data)
            except Exception as e:
                print(f"포트폴리오 로드 실패: {e}")
    
    def save_portfolios(self):
        """포트폴리오를 파일에 저장"""
        try:
            data = {user_id: portfolio.to_dict() for user_id, portfolio in self.portfolios.items()}
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"포트폴리오 저장 실패: {e}")
    
    def get_portfolio(self, user_id: str) -> Portfolio:
        """사용자 포트폴리오 조회 또는 생성"""
        if user_id not in self.portfolios:
            self.portfolios[user_id] = Portfolio(user_id=user_id, positions={})
        return self.portfolios[user_id]
    
    def add_position(self, user_id: str, ticker: str, quantity: float, 
                    average_price: float, currency: str = "USD", sector: str = "") -> Position:
        """포지션 추가"""
        portfolio = self.get_portfolio(user_id)
        position = portfolio.add_position(ticker, quantity, average_price, currency, sector)
        self.save_portfolios()
        return position
    
    def update_position_price(self, user_id: str, ticker: str, current_price: float) -> Optional[Position]:
        """포지션 현재가 업데이트"""
        portfolio = self.get_portfolio(user_id)
        position = portfolio.update_position(ticker, current_price)
        if position:
            self.save_portfolios()
        return position
    
    def remove_position(self, user_id: str, ticker: str) -> Optional[Position]:
        """포지션 제거"""
        portfolio = self.get_portfolio(user_id)
        position = portfolio.remove_position(ticker)
        if position:
            self.save_portfolios()
        return position
    
    def get_position(self, user_id: str, ticker: str) -> Optional[Position]:
        """포지션 조회"""
        portfolio = self.get_portfolio(user_id)
        return portfolio.get_position(ticker)
    
    def get_portfolio_summary(self, user_id: str) -> Dict[str, Any]:
        """포트폴리오 요약"""
        portfolio = self.get_portfolio(user_id)
        return {
            "user_id": user_id,
            "total_positions": len(portfolio.positions),
            "total_invested": portfolio.total_invested,
            "total_market_value": portfolio.total_market_value,
            "total_unrealized_pnl": portfolio.total_unrealized_pnl,
            "total_unrealized_pnl_percent": portfolio.total_unrealized_pnl_percent,
            "sector_allocation": portfolio.get_sector_allocation(),
            "last_updated": portfolio.last_updated.isoformat()
        }
    
    def get_positions_list(self, user_id: str) -> List[Dict[str, Any]]:
        """포지션 목록"""
        portfolio = self.get_portfolio(user_id)
        positions = []
        for ticker, position in portfolio.positions.items():
            positions.append({
                "ticker": ticker,
                "quantity": position.quantity,
                "average_price": position.average_price,
                "current_price": position.current_price,
                "market_value": position.market_value,
                "unrealized_pnl": position.unrealized_pnl,
                "unrealized_pnl_percent": position.unrealized_pnl_percent,
                "sector": position.sector,
                "last_updated": position.last_updated.isoformat()
            })
        return positions

# 전역 포트폴리오 관리자 인스턴스
portfolio_manager = PortfolioManager()
