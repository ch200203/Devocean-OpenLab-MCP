"""
A2A (AI-to-AI) 모듈 - 에이전트 간 통신
"""

from .a2a_protocol import (
    A2AMessage, MessageType, AgentRole, Priority,
    StockAnalysisRequest, StockAnalysisResponse,
    PortfolioAnalysisRequest, PortfolioAnalysisResponse,
    RiskEventRequest, RiskEventResponse,
    AgentCapability, A2AProtocol
)
from .a2a_adapter import (
    A2ATransport, WebSocketTransport, HTTPTransport,
    A2AAdapter, InvestmentA2AAdapter, RiskA2AAdapter, PortfolioA2AAdapter
)
from .a2a_integration import A2AIntegrationManager, a2a_manager

__all__ = [
    'A2AMessage', 'MessageType', 'AgentRole', 'Priority',
    'StockAnalysisRequest', 'StockAnalysisResponse',
    'PortfolioAnalysisRequest', 'PortfolioAnalysisResponse', 
    'RiskEventRequest', 'RiskEventResponse',
    'AgentCapability', 'A2AProtocol',
    'A2ATransport', 'WebSocketTransport', 'HTTPTransport',
    'A2AAdapter', 'InvestmentA2AAdapter', 'RiskA2AAdapter', 'PortfolioA2AAdapter',
    'A2AIntegrationManager', 'a2a_manager'
]
