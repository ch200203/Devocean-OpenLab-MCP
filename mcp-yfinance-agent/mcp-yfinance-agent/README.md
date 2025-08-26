# 주식 시세 조회 AI Agent (MCP)

Yahoo Finance를 통해 주식 시세 정보를 조회하는 AI 에이전트입니다. Cursor MCP를 통해 사용할 수 있습니다.

## 기능

- 실시간 주식 가격 조회
- 주식 히스토리 데이터 조회 (OHLCV)
- 자연어 질의 응답
- Cursor MCP 통합

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

`env.example` 파일을 복사하여 `.env` 파일을 생성하고 필요한 설정을 입력하세요:

```bash
cp env.example .env
```

`.env` 파일에서 다음 설정을 확인/수정하세요:

```env
# LLM 설정 (무료 사용)
LLM_ID=cursor:auto
# OPENAI_API_KEY=your_openai_api_key_here  # Cursor Auto 사용시 불필요

# MCP 서버 설정
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000

# Yahoo Finance 설정
YF_TIMEOUT=10
YF_RETRY_COUNT=3

# 에이전트 설정
AGENT_MAX_ITERATIONS=10
AGENT_VERBOSE=true
```

## 사용법

### 1. 직접 실행

```bash
cd src
python agent_graph.py
```

### 2. Cursor MCP를 통한 사용

Cursor에서 MCP 서버로 등록하여 사용할 수 있습니다:

1. Cursor 설정에서 MCP 서버 추가:
   - 서버 이름: `stock-agent`
   - 명령어: `python`
   - 인수: `["./src/cursor_mcp_server.py"]`
   - 트랜스포트: `stdio`

2. Cursor에서 사용 예시:
   ```
   /ask_stock_agent "AAPL 최신 가격을 알려주고, 최근 5일 일봉 OHLC를 요약해줘"
   ```

## API 도구

### Yahoo Finance MCP 서버 (`mcp_yfinance_server.py`)

- `get_quote(ticker: str)`: 최신 주식 가격 정보 조회
- `get_history(ticker: str, period: str, interval: str, limit: int)`: 주식 히스토리 데이터 조회

### Stock Agent MCP 서버 (`cursor_mcp_server.py`)

- `ask_stock_agent(query: str, max_iterations: int)`: AI 에이전트에게 질문
- `get_agent_info()`: 에이전트 정보 조회

## 예시 질의

- "AAPL 최신 가격을 알려주고, 최근 5일 일봉 OHLC를 요약해줘"
- "TSLA의 1개월 주가 변동을 분석해줘"
- "MSFT와 GOOGL의 현재 가격을 비교해줘"

## 파일 구조

```
src/
├── agent_graph.py          # 메인 에이전트 로직
├── mcp_yfinance_server.py  # Yahoo Finance MCP 서버
├── cursor_mcp_server.py    # Cursor MCP 서버
└── config.py              # 환경변수 설정
```

## LLM 설정 옵션

### 1. Cursor Auto (무료, 권장)
```env
LLM_ID=cursor:auto
```
- OpenAI API 키 불필요
- Cursor 내장 LLM 사용
- 무료로 사용 가능

### 2. OpenAI (유료)
```env
LLM_ID=openai:gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key_here
```
- OpenAI API 키 필요
- 유료 서비스

## 주의사항

- Cursor Auto 사용시 OpenAI API 키가 필요하지 않습니다
- Yahoo Finance API의 응답 시간에 따라 지연이 있을 수 있습니다
- 네트워크 연결이 필요합니다 