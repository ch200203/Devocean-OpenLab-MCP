### 1) 사전 요구사항
- Docker, Docker Compose 설치
- OpenAI API 키 보유
d
### 2) 환경 변수 설정 (.env)
프로젝트 루트의 `.env` 파일을 생성(또는 기존 파일 수정) 후 OpenAI 키를 개인적으로 넣어줘야 합니다.

```bash
cp env.example .env
# 편집: OPENAI_API_KEY 입력, LLM_ID 확인 (기본 openai:gpt-4o-mini)
```

`.env` 주요 항목:
- `LLM_ID=openai:gpt-4o-mini`
- `OPENAI_API_KEY=sk-...` (필수)

### 3) 이미지 빌드
루트에서 다음을 실행합니다.

```bash
docker compose build
```

생성되는 서비스 이미지:
- `yfinance`: MCP(Yahoo Finance)
- `risk`: MCP(Risk Event)
- `stock_agent`: MCP(Stock Agent)
- `a2a`: A2A 통합(WebSocket, 포트 8766/8767/8768)

### 4) 컨테이너 기동

```bash
docker compose up -d
```

상태 확인:
```bash
docker compose ps
```

로그 확인(A2A):
```bash
docker compose logs -f a2a
```

### 5) A2A WebSocket 테스트 (간단 헬스)
A2A 통합 서버는 투자/리스크/포트폴리오 어댑터를 8766/8767/8768에서 서비스합니다.

간단 연결 테스트(예: 8766):
```bash
# websocat 설치되어 있다면
websocat ws://localhost:8766
```

또는 Python으로 연결 시도:
```python
import asyncio, websockets

async def ping():
    uri = "ws://localhost:8766"
    async with websockets.connect(uri) as ws:
        await ws.send("{\"message_type\":\"heartbeat\"}")
        try:
            resp = await asyncio.wait_for(ws.recv(), timeout=5)
            print("recv:", resp)
        except asyncio.TimeoutError:
            print("no response (ok for simple smoke test)")

asyncio.run(ping())
```

### 6) 샘플 요청 보내기
가이드 문서 `A2A_INTEGRATION_GUIDE.md`의 예시를 참고하여 투자/리스크/포트폴리오 요청을 보낼 수 있습니다.

예: 투자 분석 요청(8766):
```python
import asyncio, websockets, json
from datetime import datetime
import time

async def request_stock_analysis(ticker: str):
    message = {
        "message_id": f"msg_{int(time.time())}",
        "sender_id": "tester",
        "receiver_id": "investment_agent_001",
        "message_type": "request",
        "priority": "high",
        "timestamp": datetime.now().isoformat(),
        "payload": {
            "ticker": ticker,
            "analysis_type": "comprehensive",
            "timeframe": "1m",
            "user_profile": {"risk_tolerance": "moderate"}
        }
    }
    async with websockets.connect("ws://localhost:8766") as ws:
        await ws.send(json.dumps(message))
        resp = await ws.recv()
        print("response:", resp)

asyncio.run(request_stock_analysis("AAPL"))
```

### 7) 종료/정리
```bash
docker compose down
```

### 참고
- `.env`의 `LLM_ID`를 변경하면 모델 전환 가능(OpenAI/Ollama 등).
- MCP 컨테이너는 내부 네트워크로만 동작하며, 외부 노출은 A2A 포트(8766/8767/8768)만 수행합니다.


