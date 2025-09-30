#!/usr/bin/env python3
"""
A2A 어댑터 및 인터페이스 구현
다른 AI 에이전트와의 통신을 담당하는 어댑터
"""

import asyncio
import json
import websockets
import httpx
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime, timedelta
import logging
from abc import ABC, abstractmethod

from a2a_protocol import (
    A2AMessage, MessageType, AgentRole, Priority, 
    StockAnalysisRequest, StockAnalysisResponse,
    PortfolioAnalysisRequest, PortfolioAnalysisResponse,
    RiskEventRequest, RiskEventResponse,
    AgentCapability, A2AProtocol
)

logger = logging.getLogger(__name__)

class A2ATransport(ABC):
    """A2A 통신 전송 계층 인터페이스"""
    
    @abstractmethod
    async def send_message(self, message: A2AMessage) -> bool:
        """메시지 전송"""
        pass
    
    @abstractmethod
    async def receive_message(self) -> Optional[A2AMessage]:
        """메시지 수신"""
        pass
    
    @abstractmethod
    async def start_server(self, port: int, message_handler: Callable[[A2AMessage], Awaitable[None]]):
        """서버 시작"""
        pass
    
    @abstractmethod
    async def connect(self, endpoint: str) -> bool:
        """연결"""
        pass

class WebSocketTransport(A2ATransport):
    """WebSocket 기반 A2A 통신"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.websocket = None
        self.server = None
        self.message_handler = None
    
    async def send_message(self, message: A2AMessage) -> bool:
        """WebSocket을 통한 메시지 전송"""
        try:
            if self.websocket and not self.websocket.closed:
                message_str = message.sender_id + ":" + json.dumps(message.to_dict())
                await self.websocket.send(message_str)
                logger.info(f"Message sent to {message.receiver_id}: {message.message_type.value}")
                return True
            else:
                logger.error("WebSocket connection not available")
                return False
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    async def receive_message(self) -> Optional[A2AMessage]:
        """WebSocket을 통한 메시지 수신"""
        try:
            if self.websocket and not self.websocket.closed:
                message_str = await self.websocket.recv()
                sender_id, message_data = message_str.split(":", 1)
                message_dict = json.loads(message_data)
                message = A2AMessage.from_dict(message_dict)
                return message
        except Exception as e:
            logger.error(f"Failed to receive message: {e}")
        return None
    
    async def start_server(self, port: int, message_handler: Callable[[A2AMessage], Awaitable[None]]):
        """WebSocket 서버 시작"""
        self.message_handler = message_handler
        
        async def handle_client(websocket, path):
            self.websocket = websocket
            logger.info(f"A2A client connected: {websocket.remote_address}")
            
            try:
                async for message_str in websocket:
                    try:
                        sender_id, message_data = message_str.split(":", 1)
                        message_dict = json.loads(message_data)
                        message = A2AMessage.from_dict(message_dict)
                        
                        if message.receiver_id == self.agent_id:
                            await message_handler(message)
                        else:
                            logger.warning(f"Message not for this agent: {message.receiver_id}")
                            
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        
            except websockets.exceptions.ConnectionClosed:
                logger.info("A2A client disconnected")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
        
        # 컨테이너 외부 접근을 위해 0.0.0.0 바인딩
        self.server = await websockets.serve(handle_client, "0.0.0.0", port)
        logger.info(f"A2A WebSocket server started on port {port}")
    
    async def connect(self, endpoint: str) -> bool:
        """WebSocket 서버에 연결"""
        try:
            self.websocket = await websockets.connect(endpoint)
            logger.info(f"Connected to A2A server: {endpoint}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to A2A server: {e}")
            return False

class HTTPTransport(A2ATransport):
    """HTTP 기반 A2A 통신"""
    
    def __init__(self, agent_id: str, base_url: str = "http://localhost:8000"):
        self.agent_id = agent_id
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def send_message(self, message: A2AMessage) -> bool:
        """HTTP를 통한 메시지 전송"""
        try:
            response = await self.client.post(
                f"{self.base_url}/a2a/message",
                json=message.to_dict()
            )
            response.raise_for_status()
            logger.info(f"HTTP message sent to {message.receiver_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send HTTP message: {e}")
            return False
    
    async def receive_message(self) -> Optional[A2AMessage]:
        """HTTP를 통한 메시지 수신 (폴링 방식)"""
        try:
            response = await self.client.get(
                f"{self.base_url}/a2a/messages/{self.agent_id}"
            )
            response.raise_for_status()
            messages = response.json()
            
            if messages:
                # 가장 오래된 메시지부터 처리
                message_data = messages[0]
                message = A2AMessage.from_dict(message_data)
                return message
        except Exception as e:
            logger.error(f"Failed to receive HTTP message: {e}")
        return None
    
    async def start_server(self, port: int, message_handler: Callable[[A2AMessage], Awaitable[None]]):
        """HTTP 서버는 별도 구현 필요 (FastAPI 등)"""
        raise NotImplementedError("HTTP server requires separate implementation")
    
    async def connect(self, endpoint: str) -> bool:
        """HTTP 엔드포인트 연결 테스트"""
        try:
            response = await self.client.get(f"{endpoint}/health")
            response.raise_for_status()
            logger.info(f"Connected to A2A HTTP server: {endpoint}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to A2A HTTP server: {e}")
            return False

class A2AAdapter:
    """A2A 어댑터 메인 클래스"""
    
    def __init__(self, agent_id: str, agent_role: AgentRole, transport_type: str = "websocket"):
        self.agent_id = agent_id
        self.agent_role = agent_role
        self.protocol = A2AProtocol(agent_id, agent_role)
        self.transport = self._create_transport(transport_type)
        self.capabilities = None
        self.registered_agents = {}
        self.pending_requests = {}
        self.message_handlers = {}
        
        # 기본 메시지 핸들러 등록
        self._register_default_handlers()
    
    def _create_transport(self, transport_type: str) -> A2ATransport:
        """전송 계층 생성"""
        if transport_type == "websocket":
            return WebSocketTransport(self.agent_id)
        elif transport_type == "http":
            return HTTPTransport(self.agent_id)
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")
    
    def _register_default_handlers(self):
        """기본 메시지 핸들러 등록"""
        self.register_handler(MessageType.REQUEST, self._handle_request)
        self.register_handler(MessageType.RESPONSE, self._handle_response)
        self.register_handler(MessageType.ERROR, self._handle_error)
        self.register_handler(MessageType.HEARTBEAT, self._handle_heartbeat)
        self.register_handler(MessageType.REGISTRATION, self._handle_registration)
        self.register_handler(MessageType.CAPABILITY_QUERY, self._handle_capability_query)
    
    def register_capabilities(self, capabilities: AgentCapability):
        """에이전트 능력 등록"""
        self.capabilities = capabilities
        self.protocol.register_capabilities(capabilities)
        logger.info(f"Agent {self.agent_id} capabilities registered: {capabilities.role.value}")
    
    def register_handler(self, message_type: MessageType, handler: Callable[[A2AMessage], Awaitable[None]]):
        """메시지 핸들러 등록"""
        self.message_handlers[message_type] = handler
        logger.info(f"Handler registered for {message_type.value}")
    
    async def start_server(self, port: int):
        """A2A 서버 시작"""
        await self.transport.start_server(port, self._handle_message)
        logger.info(f"A2A adapter server started on port {port}")
    
    async def connect_to_registry(self, registry_endpoint: str):
        """레지스트리에 연결 및 등록"""
        if not self.capabilities:
            raise ValueError("Capabilities must be registered before connecting to registry")
        
        # 레지스트리에 연결
        if await self.transport.connect(registry_endpoint):
            # 에이전트 등록
            registration_msg = self.protocol.get_registration_message()
            await self.transport.send_message(registration_msg)
            logger.info(f"Agent {self.agent_id} registered with registry")
    
    async def discover_agents(self, target_role: Optional[AgentRole] = None) -> List[Dict[str, Any]]:
        """다른 에이전트 탐색"""
        query_msg = self.protocol.get_capability_query_message(target_role)
        await self.transport.send_message(query_msg)
        
        # 응답 대기 (실제 구현에서는 더 정교한 대기 메커니즘 필요)
        await asyncio.sleep(1)
        return list(self.registered_agents.values())
    
    async def request_stock_analysis(self, target_agent_id: str, ticker: str, 
                                   analysis_type: str, timeframe: str = "1m",
                                   user_profile: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """주식 분석 요청"""
        request_msg = self.protocol.create_stock_analysis_request(
            target_agent_id, ticker, analysis_type, timeframe, user_profile
        )
        
        # 요청 저장 (응답 매칭용)
        self.pending_requests[request_msg.message_id] = {
            "request": request_msg,
            "timestamp": datetime.now(),
            "type": "stock_analysis"
        }
        
        # 메시지 전송
        if await self.transport.send_message(request_msg):
            # 응답 대기 (실제 구현에서는 콜백 기반으로 처리)
            return await self._wait_for_response(request_msg.message_id, timeout=30)
        
        return None
    
    async def request_portfolio_analysis(self, target_agent_id: str, user_id: str,
                                       portfolio_data: Dict[str, Any],
                                       analysis_goals: List[str]) -> Optional[Dict[str, Any]]:
        """포트폴리오 분석 요청"""
        request_msg = self.protocol.create_portfolio_analysis_request(
            target_agent_id, user_id, portfolio_data, analysis_goals
        )
        
        # 요청 저장
        self.pending_requests[request_msg.message_id] = {
            "request": request_msg,
            "timestamp": datetime.now(),
            "type": "portfolio_analysis"
        }
        
        # 메시지 전송
        if await self.transport.send_message(request_msg):
            return await self._wait_for_response(request_msg.message_id, timeout=30)
        
        return None
    
    async def request_risk_analysis(self, target_agent_id: str, ticker: str,
                                  event_sources: List[str] = None,
                                  time_horizon: str = "1d") -> Optional[Dict[str, Any]]:
        """리스크 분석 요청"""
        request_msg = self.protocol.create_risk_analysis_request(
            target_agent_id, ticker, event_sources, time_horizon
        )
        
        # 요청 저장
        self.pending_requests[request_msg.message_id] = {
            "request": request_msg,
            "timestamp": datetime.now(),
            "type": "risk_analysis"
        }
        
        # 메시지 전송
        if await self.transport.send_message(request_msg):
            return await self._wait_for_response(request_msg.message_id, timeout=30)
        
        return None
    
    async def _handle_message(self, message: A2AMessage):
        """들어오는 메시지 처리"""
        logger.info(f"Received message: {message.message_type.value} from {message.sender_id}")
        
        # 메시지 타입별 핸들러 호출
        handler = self.message_handlers.get(message.message_type)
        if handler:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                # 에러 응답 전송
                error_response = self.protocol.create_error_response(
                    message, str(e), "HANDLER_ERROR"
                )
                await self.transport.send_message(error_response)
        else:
            logger.warning(f"No handler for message type: {message.message_type.value}")
    
    async def _handle_request(self, message: A2AMessage):
        """요청 메시지 처리 (서브클래스에서 구현)"""
        logger.info(f"Handling request from {message.sender_id}")
        # 실제 구현은 각 에이전트에서 오버라이드
    
    async def _handle_response(self, message: A2AMessage):
        """응답 메시지 처리"""
        correlation_id = message.correlation_id
        if correlation_id and correlation_id in self.pending_requests:
            # 대기 중인 요청에 응답 저장
            self.pending_requests[correlation_id]["response"] = message.payload
            logger.info(f"Response received for request {correlation_id}")
    
    async def _handle_error(self, message: A2AMessage):
        """에러 메시지 처리"""
        correlation_id = message.correlation_id
        if correlation_id and correlation_id in self.pending_requests:
            # 대기 중인 요청에 에러 저장
            self.pending_requests[correlation_id]["error"] = message.payload
            logger.error(f"Error received for request {correlation_id}: {message.payload}")
    
    async def _handle_heartbeat(self, message: A2AMessage):
        """하트비트 메시지 처리"""
        logger.debug(f"Heartbeat from {message.sender_id}")
        # 하트비트 응답 (선택사항)
    
    async def _handle_registration(self, message: A2AMessage):
        """에이전트 등록 처리"""
        if message.sender_id != self.agent_id:  # 자신의 등록 메시지는 무시
            capability_data = message.payload
            self.registered_agents[message.sender_id] = capability_data
            logger.info(f"Agent registered: {message.sender_id} - {capability_data.get('role', 'unknown')}")
    
    async def _handle_capability_query(self, message: A2AMessage):
        """능력 조회 처리"""
        # 자신의 능력 정보 응답
        if self.capabilities:
            response = self.protocol.create_response(message, asdict(self.capabilities))
            await self.transport.send_message(response)
    
    async def _wait_for_response(self, request_id: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """응답 대기"""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            if request_id in self.pending_requests:
                pending = self.pending_requests[request_id]
                
                if "response" in pending:
                    response_data = pending["response"]
                    del self.pending_requests[request_id]
                    return response_data
                elif "error" in pending:
                    error_data = pending["error"]
                    del self.pending_requests[request_id]
                    logger.error(f"Request {request_id} failed: {error_data}")
                    return None
            
            await asyncio.sleep(0.1)
        
        # 타임아웃
        if request_id in self.pending_requests:
            del self.pending_requests[request_id]
        logger.warning(f"Request {request_id} timed out")
        return None
    
    async def send_heartbeat(self, target_agent_id: str):
        """하트비트 전송"""
        heartbeat_msg = self.protocol.create_message(
            target_agent_id, MessageType.HEARTBEAT, {"timestamp": datetime.now().isoformat()}
        )
        await self.transport.send_message(heartbeat_msg)
    
    async def cleanup_expired_requests(self):
        """만료된 요청 정리"""
        current_time = datetime.now()
        expired_requests = []
        
        for request_id, pending in self.pending_requests.items():
            if (current_time - pending["timestamp"]).seconds > 300:  # 5분
                expired_requests.append(request_id)
        
        for request_id in expired_requests:
            del self.pending_requests[request_id]
            logger.info(f"Cleaned up expired request: {request_id}")

# 특화된 어댑터들
class InvestmentA2AAdapter(A2AAdapter):
    """투자 분석 에이전트용 A2A 어댑터"""
    
    def __init__(self, transport_type: str = "websocket"):
        super().__init__("investment_agent_001", AgentRole.INVESTMENT_ANALYST, transport_type)
        
        # 투자 분석 관련 핸들러 등록
        self.register_handler(MessageType.REQUEST, self._handle_investment_request)
    
    async def _handle_investment_request(self, message: A2AMessage):
        """투자 분석 요청 처리"""
        payload = message.payload
        
        if "ticker" in payload and "analysis_type" in payload:
            # 주식 분석 요청 처리
            ticker = payload["ticker"]
            analysis_type = payload["analysis_type"]
            
            # 실제 분석 로직 호출 (기존 에이전트와 연동)
            try:
                from agent_graph import investment_agent
                analysis_result = await investment_agent.process_query(
                    f"{ticker} {analysis_type} 분석해줘"
                )
                
                # 응답 생성
                response = self.protocol.create_response(message, analysis_result)
                await self.transport.send_message(response)
                
            except Exception as e:
                error_response = self.protocol.create_error_response(message, str(e))
                await self.transport.send_message(error_response)

class RiskA2AAdapter(A2AAdapter):
    """리스크 분석 에이전트용 A2A 어댑터"""
    
    def __init__(self, transport_type: str = "websocket"):
        super().__init__("risk_agent_001", AgentRole.RISK_ASSESSOR, transport_type)
        
        # 리스크 분석 관련 핸들러 등록
        self.register_handler(MessageType.REQUEST, self._handle_risk_request)
    
    async def _handle_risk_request(self, message: A2AMessage):
        """리스크 분석 요청 처리"""
        payload = message.payload
        
        if "ticker" in payload:
            ticker = payload["ticker"]
            
            # 리스크 분석 실행
            try:
                from risk_analyzer_standalone import RiskEventDetector
                detector = RiskEventDetector()
                analysis = detector.analyze_ticker_risk(ticker)
                
                # 응답 데이터 구성
                response_data = {
                    "ticker": analysis.ticker,
                    "overall_risk_score": analysis.overall_risk_score,
                    "risk_level": analysis.risk_level,
                    "total_events": analysis.total_events,
                    "high_risk_events": analysis.high_risk_events,
                    "risk_factors": analysis.risk_factors,
                    "recommendation": analysis.recommendation,
                    "recent_events": [asdict(event) for event in analysis.recent_events]
                }
                
                # 응답 생성
                response = self.protocol.create_response(message, response_data)
                await self.transport.send_message(response)
                
            except Exception as e:
                error_response = self.protocol.create_error_response(message, str(e))
                await self.transport.send_message(error_response)

class PortfolioA2AAdapter(A2AAdapter):
    """포트폴리오 관리 에이전트용 A2A 어댑터"""
    
    def __init__(self, transport_type: str = "websocket"):
        super().__init__("portfolio_agent_001", AgentRole.PORTFOLIO_MANAGER, transport_type)
        
        # 포트폴리오 관리 관련 핸들러 등록
        self.register_handler(MessageType.REQUEST, self._handle_portfolio_request)
    
    async def _handle_portfolio_request(self, message: A2AMessage):
        """포트폴리오 분석 요청 처리"""
        payload = message.payload
        
        if "user_id" in payload and "portfolio_data" in payload:
            user_id = payload["user_id"]
            portfolio_data = payload["portfolio_data"]
            
            # 포트폴리오 분석 실행
            try:
                from portfolio_analyzer import portfolio_analyzer
                from memory_manager import memory_manager
                
                profile = memory_manager.get_user_profile(user_id)
                analysis = portfolio_analyzer.analyze_portfolio(user_id, profile)
                
                # 응답 데이터 구성
                response_data = {
                    "user_id": user_id,
                    "overall_score": analysis.total_unrealized_pnl_percent,
                    "risk_metrics": analysis.risk_metrics,
                    "performance_metrics": analysis.performance_metrics,
                    "recommendations": analysis.recommendations,
                    "sector_allocation": analysis.sector_allocation
                }
                
                # 응답 생성
                response = self.protocol.create_response(message, response_data)
                await self.transport.send_message(response)
                
            except Exception as e:
                error_response = self.protocol.create_error_response(message, str(e))
                await self.transport.send_message(error_response)
