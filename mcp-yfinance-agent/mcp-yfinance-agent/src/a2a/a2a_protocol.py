#!/usr/bin/env python3
"""
A2A (AI-to-AI) 통신 프로토콜 정의
다른 AI 에이전트와의 표준화된 통신 인터페이스
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
import uuid

class MessageType(Enum):
    """A2A 메시지 타입"""
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    REGISTRATION = "registration"
    CAPABILITY_QUERY = "capability_query"
    CAPABILITY_RESPONSE = "capability_response"

class AgentRole(Enum):
    """AI 에이전트 역할"""
    INVESTMENT_ANALYST = "investment_analyst"
    RISK_ASSESSOR = "risk_assessor"
    PORTFOLIO_MANAGER = "portfolio_manager"
    MARKET_RESEARCHER = "market_researcher"
    NEWS_ANALYZER = "news_analyzer"
    TECHNICAL_ANALYST = "technical_analyst"
    FUNDAMENTAL_ANALYST = "fundamental_analyst"

class Priority(Enum):
    """메시지 우선순위"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class AgentCapability:
    """에이전트 능력 정의"""
    role: AgentRole
    capabilities: List[str]
    supported_tickers: List[str]
    supported_timeframes: List[str]
    max_concurrent_requests: int
    response_time_avg: float  # 평균 응답 시간 (초)
    version: str

@dataclass
class A2AMessage:
    """A2A 통신 메시지"""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    priority: Priority
    timestamp: datetime
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['message_type'] = self.message_type.value
        data['priority'] = self.priority.value
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """딕셔너리에서 생성"""
        data['message_type'] = MessageType(data['message_type'])
        data['priority'] = Priority(data['priority'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)

@dataclass
class StockAnalysisRequest:
    """주식 분석 요청"""
    ticker: str
    analysis_type: str  # "technical", "fundamental", "risk", "comprehensive"
    timeframe: str  # "1d", "1w", "1m", "3m", "1y"
    user_profile: Optional[Dict[str, Any]] = None
    additional_context: Optional[Dict[str, Any]] = None

@dataclass
class StockAnalysisResponse:
    """주식 분석 응답"""
    ticker: str
    analysis_type: str
    confidence_score: float  # 0.0 - 1.0
    analysis_result: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    risk_assessment: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class PortfolioAnalysisRequest:
    """포트폴리오 분석 요청"""
    user_id: str
    portfolio_data: Dict[str, Any]
    analysis_goals: List[str]  # ["risk_assessment", "optimization", "rebalancing"]
    constraints: Optional[Dict[str, Any]] = None

@dataclass
class PortfolioAnalysisResponse:
    """포트폴리오 분석 응답"""
    user_id: str
    overall_score: float  # 0.0 - 100.0
    risk_metrics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    rebalancing_suggestions: Optional[List[Dict[str, Any]]] = None

@dataclass
class RiskEventRequest:
    """리스크 이벤트 분석 요청"""
    ticker: str
    event_sources: List[str]  # ["news", "social_media", "financial_reports", "market_data"]
    time_horizon: str  # "1h", "1d", "1w", "1m"
    severity_threshold: str  # "low", "medium", "high", "critical"

@dataclass
class RiskEventResponse:
    """리스크 이벤트 분석 응답"""
    ticker: str
    overall_risk_score: float  # 0.0 - 100.0
    risk_level: str
    detected_events: List[Dict[str, Any]]
    risk_factors: List[str]
    recommendations: List[str]
    confidence_score: float

class A2AProtocol:
    """A2A 통신 프로토콜 관리"""
    
    def __init__(self, agent_id: str, agent_role: AgentRole):
        self.agent_id = agent_id
        self.agent_role = agent_role
        self.capabilities = None
        self.registered_agents = {}
    
    def create_message(self, receiver_id: str, message_type: MessageType, 
                      payload: Dict[str, Any], priority: Priority = Priority.NORMAL,
                      correlation_id: Optional[str] = None) -> A2AMessage:
        """메시지 생성"""
        return A2AMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            priority=priority,
            timestamp=datetime.now(),
            payload=payload,
            correlation_id=correlation_id
        )
    
    def create_stock_analysis_request(self, receiver_id: str, ticker: str, 
                                    analysis_type: str, timeframe: str = "1m",
                                    user_profile: Optional[Dict[str, Any]] = None) -> A2AMessage:
        """주식 분석 요청 생성"""
        request = StockAnalysisRequest(
            ticker=ticker,
            analysis_type=analysis_type,
            timeframe=timeframe,
            user_profile=user_profile
        )
        
        return self.create_message(
            receiver_id=receiver_id,
            message_type=MessageType.REQUEST,
            payload=asdict(request),
            priority=Priority.HIGH
        )
    
    def create_portfolio_analysis_request(self, receiver_id: str, user_id: str,
                                        portfolio_data: Dict[str, Any],
                                        analysis_goals: List[str]) -> A2AMessage:
        """포트폴리오 분석 요청 생성"""
        request = PortfolioAnalysisRequest(
            user_id=user_id,
            portfolio_data=portfolio_data,
            analysis_goals=analysis_goals
        )
        
        return self.create_message(
            receiver_id=receiver_id,
            message_type=MessageType.REQUEST,
            payload=asdict(request),
            priority=Priority.HIGH
        )
    
    def create_risk_analysis_request(self, receiver_id: str, ticker: str,
                                   event_sources: List[str] = None,
                                   time_horizon: str = "1d") -> A2AMessage:
        """리스크 분석 요청 생성"""
        if event_sources is None:
            event_sources = ["news", "financial_reports", "market_data"]
            
        request = RiskEventRequest(
            ticker=ticker,
            event_sources=event_sources,
            time_horizon=time_horizon,
            severity_threshold="medium"
        )
        
        return self.create_message(
            receiver_id=receiver_id,
            message_type=MessageType.REQUEST,
            payload=asdict(request),
            priority=Priority.HIGH
        )
    
    def create_response(self, original_message: A2AMessage, 
                       response_data: Dict[str, Any]) -> A2AMessage:
        """응답 메시지 생성"""
        return A2AMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            receiver_id=original_message.sender_id,
            message_type=MessageType.RESPONSE,
            priority=original_message.priority,
            timestamp=datetime.now(),
            payload=response_data,
            correlation_id=original_message.message_id
        )
    
    def create_error_response(self, original_message: A2AMessage, 
                            error_message: str, error_code: str = "UNKNOWN_ERROR") -> A2AMessage:
        """에러 응답 생성"""
        return A2AMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            receiver_id=original_message.sender_id,
            message_type=MessageType.ERROR,
            priority=Priority.HIGH,
            timestamp=datetime.now(),
            payload={
                "error_code": error_code,
                "error_message": error_message,
                "original_request": original_message.payload
            },
            correlation_id=original_message.message_id
        )
    
    def serialize_message(self, message: A2AMessage) -> str:
        """메시지를 JSON 문자열로 직렬화"""
        return json.dumps(message.to_dict(), ensure_ascii=False, indent=2)
    
    def deserialize_message(self, message_str: str) -> A2AMessage:
        """JSON 문자열을 메시지로 역직렬화"""
        data = json.loads(message_str)
        return A2AMessage.from_dict(data)
    
    def register_capabilities(self, capabilities: AgentCapability):
        """에이전트 능력 등록"""
        self.capabilities = capabilities
    
    def get_registration_message(self) -> A2AMessage:
        """등록 메시지 생성"""
        if not self.capabilities:
            raise ValueError("Capabilities must be registered first")
        
        return self.create_message(
            receiver_id="registry",
            message_type=MessageType.REGISTRATION,
            payload=asdict(self.capabilities),
            priority=Priority.NORMAL
        )
    
    def get_capability_query_message(self, target_role: Optional[AgentRole] = None) -> A2AMessage:
        """능력 조회 메시지 생성"""
        payload = {}
        if target_role:
            payload["target_role"] = target_role.value
        
        return self.create_message(
            receiver_id="registry",
            message_type=MessageType.CAPABILITY_QUERY,
            payload=payload,
            priority=Priority.LOW
        )

# 전역 프로토콜 인스턴스 (각 에이전트별로 생성)
investment_protocol = A2AProtocol(
    agent_id="investment_agent_001",
    agent_role=AgentRole.INVESTMENT_ANALYST
)

risk_protocol = A2AProtocol(
    agent_id="risk_agent_001", 
    agent_role=AgentRole.RISK_ASSESSOR
)

portfolio_protocol = A2AProtocol(
    agent_id="portfolio_agent_001",
    agent_role=AgentRole.PORTFOLIO_MANAGER
)
