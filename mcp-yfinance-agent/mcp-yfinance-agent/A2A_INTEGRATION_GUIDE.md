# A2A (AI-to-AI) 연동 가이드

## 📋 개요

이 문서는 다른 AI 에이전트들이 우리의 투자 분석 시스템과 A2A(AI-to-AI) 통신을 통해 연동할 수 있도록 하는 가이드입니다.

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   외부 AI       │    │   외부 AI       │    │   외부 AI       │
│   에이전트 A    │    │   에이전트 B    │    │   에이전트 C    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │     A2A Protocol     │                      │
          │     (WebSocket/HTTP) │                      │
          └────────────┬─────────┼──────────────────────┘
                       │         │
            ┌──────────▼─────────▼──────────┐
            │      A2A Integration          │
            │         Manager               │
            └──────────┬────────────────────┘
                       │
            ┌──────────▼────────────────────┐
            │    Specialized Adapters       │
            │  ┌─────────┬─────────┬───────┐│
            │  │Investment│  Risk   │Portfolio│
            │  │ Adapter  │ Adapter │Adapter ││
            │  └─────────┴─────────┴───────┘│
            └──────────┬────────────────────┘
                       │
            ┌──────────▼────────────────────┐
            │     Core AI Agents            │
            │  ┌─────────┬─────────┬───────┐│
            │  │Investment│  Risk   │Portfolio│
            │  │  Agent   │ Agent   │ Agent ││
            │  └─────────┴─────────┴───────┘│
            └────────────────────────────────┘
```

### 1. 서버 연결

우리 시스템에 연결하려면 다음 엔드포인트를 사용하세요:

```python
# WebSocket 연결
WEBSOCKET_ENDPOINTS = {
    "investment": "ws://localhost:8766",
    "risk": "ws://localhost:8767", 
    "portfolio": "ws://localhost:8768"
}

# HTTP API 연결
HTTP_ENDPOINT = "http://localhost:8000/a2a"
```

### 2. 기본 연결 예제

```python
import asyncio
import websockets
import json

async def connect_to_investment_agent():
    """투자 분석 에이전트에 연결"""
    uri = "ws://localhost:8766"
    
    async with websockets.connect(uri) as websocket:
        # 연결 확인
        print("투자 분석 에이전트에 연결됨")
        
        # 수신 대기
        async for message in websocket:
            data = json.loads(message)
            print(f"수신: {data}")
            break

# 연결 실행
asyncio.run(connect_to_investment_agent())
```

## 📡 A2A 프로토콜

### 메시지 구조

```json
{
  "message_id": "msg_1703123456_001",
  "sender_id": "your_agent_id",
  "receiver_id": "investment_agent_001",
  "message_type": "request",
  "priority": "high",
  "timestamp": "2024-12-21T10:30:00Z",
  "payload": {
    "ticker": "AAPL",
    "analysis_type": "comprehensive",
    "timeframe": "1m",
    "user_profile": {
      "risk_tolerance": "moderate",
      "investment_horizon": "short_term"
    }
  },
  "correlation_id": null,
  "expires_at": "2024-12-21T10:35:00Z"
}
```

### 메시지 타입

| 타입 | 설명 | 사용 예시 |
|------|------|-----------|
| `request` | 분석 요청 | 주식 분석, 포트폴리오 분석 |
| `response` | 분석 응답 | 분석 결과 반환 |
| `error` | 에러 응답 | 처리 실패 시 |
| `heartbeat` | 연결 상태 확인 | 주기적 연결 확인 |
| `registration` | 에이전트 등록 | 새로운 에이전트 등록 |

## 🔧 API 사용법

### 1. 주식 분석 요청

```python
async def request_stock_analysis(ticker: str, analysis_type: str = "comprehensive"):
    """주식 분석 요청"""
    
    message = {
        "message_id": f"msg_{int(time.time())}",
        "sender_id": "your_agent_id",
        "receiver_id": "investment_agent_001",
        "message_type": "request",
        "priority": "high",
        "timestamp": datetime.now().isoformat(),
        "payload": {
            "ticker": ticker,
            "analysis_type": analysis_type,  # "technical", "fundamental", "comprehensive"
            "timeframe": "1m",  # "1d", "1w", "1m", "3m", "1y"
            "user_profile": {
                "risk_tolerance": "moderate",
                "investment_horizon": "short_term",
                "trading_style": "swing_trading"
            }
        }
    }
    
    # WebSocket으로 전송
    async with websockets.connect("ws://localhost:8766") as websocket:
        await websocket.send(json.dumps(message))
        
        # 응답 수신
        response = await websocket.recv()
        result = json.loads(response)
        return result

# 사용 예시
result = await request_stock_analysis("AAPL", "comprehensive")
print(f"AAPL 분석 결과: {result}")
```

### 2. 리스크 분석 요청

```python
async def request_risk_analysis(ticker: str):
    """리스크 분석 요청"""
    
    message = {
        "message_id": f"msg_{int(time.time())}",
        "sender_id": "your_agent_id",
        "receiver_id": "risk_agent_001",
        "message_type": "request",
        "priority": "high",
        "timestamp": datetime.now().isoformat(),
        "payload": {
            "ticker": ticker,
            "event_sources": ["news", "financial_reports", "market_data"],
            "time_horizon": "1d",  # "1h", "1d", "1w", "1m"
            "severity_threshold": "medium"
        }
    }
    
    async with websockets.connect("ws://localhost:8767") as websocket:
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
        return json.loads(response)

# 사용 예시
risk_result = await request_risk_analysis("TSLA")
print(f"TSLA 리스크 분석: {risk_result}")
```

### 3. 포트폴리오 분석 요청

```python
async def request_portfolio_analysis(user_id: str, portfolio_data: dict):
    """포트폴리오 분석 요청"""
    
    message = {
        "message_id": f"msg_{int(time.time())}",
        "sender_id": "your_agent_id",
        "receiver_id": "portfolio_agent_001",
        "message_type": "request",
        "priority": "high",
        "timestamp": datetime.now().isoformat(),
        "payload": {
            "user_id": user_id,
            "portfolio_data": portfolio_data,
            "analysis_goals": ["risk_assessment", "optimization", "rebalancing"]
        }
    }
    
    async with websockets.connect("ws://localhost:8768") as websocket:
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
        return json.loads(response)

# 사용 예시
portfolio_data = {
    "positions": [
        {"ticker": "AAPL", "quantity": 100, "average_price": 150.0},
        {"ticker": "GOOGL", "quantity": 50, "average_price": 2500.0}
    ],
    "cash": 10000.0
}

portfolio_result = await request_portfolio_analysis("user123", portfolio_data)
print(f"포트폴리오 분석: {portfolio_result}")
```

## 📊 응답 형식

### 주식 분석 응답

```json
{
  "message_type": "response",
  "correlation_id": "msg_1703123456_001",
  "payload": {
    "ticker": "AAPL",
    "current_price": 193.50,
    "overall_score": 75.5,
    "risk_score": 25.0,
    "momentum_score": 80.0,
    "trend_score": 70.0,
    "recommendations": [
      {
        "action": "BUY",
        "confidence": 0.85,
        "reasoning": "강한 모멘텀과 긍정적 추세",
        "target_price": 210.0,
        "stop_loss": 180.0
      }
    ],
    "analysis_type": "comprehensive",
    "timestamp": "2024-12-21T10:30:00Z"
  }
}
```

### 리스크 분석 응답

```json
{
  "message_type": "response",
  "correlation_id": "msg_1703123456_002",
  "payload": {
    "ticker": "AAPL",
    "overall_risk_score": 24.0,
    "risk_level": "low",
    "total_events": 4,
    "high_risk_events": 0,
    "risk_factors": ["market_volatility"],
    "recommendations": [
      "낮은 리스크 상태입니다. 상대적으로 안전한 투자 환경입니다."
    ],
    "recent_events": [
      {
        "title": "AAPL 실적 발표, 예상보다 낮은 매출",
        "event_type": "market",
        "severity": "medium",
        "risk_score": 25,
        "source": "Financial News",
        "published_date": "2024-12-20T10:00:00Z"
      }
    ],
    "confidence_score": 0.8,
    "timestamp": "2024-12-21T10:30:00Z"
  }
}
```

### 포트폴리오 분석 응답

```json
{
  "message_type": "response",
  "correlation_id": "msg_1703123456_003",
  "payload": {
    "user_id": "user123",
    "overall_score": 68.5,
    "risk_metrics": {
      "portfolio_volatility": 0.25,
      "max_drawdown": 0.15,
      "sharpe_ratio": 1.2,
      "beta": 1.1
    },
    "performance_metrics": {
      "total_return": 12.5,
      "annualized_return": 15.2,
      "win_rate": 0.65
    },
    "recommendations": [
      {
        "action": "REBALANCE",
        "reasoning": "섹터 집중도가 높음",
        "confidence": 0.7
      }
    ],
    "sector_allocation": {
      "Technology": 60.0,
      "Healthcare": 25.0,
      "Finance": 15.0
    },
    "timestamp": "2024-12-21T10:30:00Z"
  }
}
```

## 🔗 HTTP API 대안

WebSocket 대신 HTTP API를 사용할 수도 있습니다:

### 주식 분석 HTTP 요청

```python
import httpx

async def http_stock_analysis(ticker: str):
    """HTTP API를 통한 주식 분석"""
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/a2a/stock_analysis",
            json={
                "ticker": ticker,
                "analysis_type": "comprehensive",
                "timeframe": "1m",
                "user_profile": {
                    "risk_tolerance": "moderate",
                    "investment_horizon": "short_term"
                }
            },
            timeout=30.0
        )
        return response.json()

# 사용 예시
result = await http_stock_analysis("AAPL")
```

### 리스크 분석 HTTP 요청

```python
async def http_risk_analysis(ticker: str):
    """HTTP API를 통한 리스크 분석"""
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/a2a/risk_analysis",
            json={
                "ticker": ticker,
                "event_sources": ["news", "financial_reports"],
                "time_horizon": "1d"
            },
            timeout=30.0
        )
        return response.json()
```

## 🔧 서버 시작 방법

### 1. A2A 서버 시작

```bash
# A2A 통합 서버 시작
cd /path/to/mcp-yfinance-agent/src
python3 a2a_integration.py

# 또는 개별 에이전트 서버 시작
python3 a2a_adapter.py --type investment --port 8766
python3 a2a_adapter.py --type risk --port 8767  
python3 a2a_adapter.py --type portfolio --port 8768
```

## 📋 에러 처리

### 일반적인 에러 코드

| 에러 코드 | 설명 | 해결 방법 |
|-----------|------|-----------|
| `CONNECTION_FAILED` | 연결 실패 | 서버 상태 확인, 엔드포인트 확인 |
| `TIMEOUT` | 요청 시간 초과 | 요청 타임아웃 증가, 서버 부하 확인 |
| `INVALID_MESSAGE` | 잘못된 메시지 형식 | 메시지 구조 검증 |
| `AGENT_NOT_FOUND` | 에이전트를 찾을 수 없음 | 에이전트 ID 확인 |
| `ANALYSIS_FAILED` | 분석 실패 | 요청 파라미터 확인 |

### 에러 응답 예제

```json
{
  "message_type": "error",
  "correlation_id": "msg_1703123456_001",
  "payload": {
    "error_code": "ANALYSIS_FAILED",
    "error_message": "종목 데이터를 찾을 수 없습니다",
    "original_request": {
      "ticker": "INVALID_TICKER",
      "analysis_type": "comprehensive"
    }
  }
}
```
