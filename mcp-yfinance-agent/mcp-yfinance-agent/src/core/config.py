import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """환경변수 설정 클래스"""
    
    # LLM 설정
    LLM_ID = os.getenv("LLM_ID", "cursor:auto")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # MCP 서버 설정
    MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "localhost")
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))
    
    # Yahoo Finance 설정
    YF_TIMEOUT = int(os.getenv("YF_TIMEOUT", "10"))
    YF_RETRY_COUNT = int(os.getenv("YF_RETRY_COUNT", "3"))
    
    # 에이전트 설정
    AGENT_MAX_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))
    AGENT_VERBOSE = os.getenv("AGENT_VERBOSE", "true").lower() == "true"

    # 기본 메시지
    DEFAULT_NOT_FOUND_MESSAGE = os.getenv(
        "DEFAULT_NOT_FOUND_MESSAGE",
        "지정된 결과를 찾을 수 없습니다. 입력을 확인하거나 다른 조건으로 다시 시도해 주세요.",
    )

    # 시스템 프롬프트 (에이전트 역할/가이드라인 사전 주입)
    SYSTEM_PROMPT = os.getenv(
        "SYSTEM_PROMPT",
        (
            "당신은 보수적 리스크 관리를 따르는 주식 분석 에이전트입니다. 이는 투자 자문이 아니며 교육 목적으로만 응답합니다.\n"
            "모호한 질의는 먼저 명확화 질문을 하세요.\n"
            "가능하면 MCP 도구로 최근 가격/히스토리(OHLCV)를 조회하여 사실 기반으로 답하세요.\n"
            "필요 시 기본 지표를 산출해 해석하세요: 단순이동평균(SMA 20/50), RSI(14), 볼린저밴드(20, 2σ), 거래량 변화.\n"
            "출력 형식:\n"
            "- 핵심 요약: 현재가, 통화, 거래소, 최근 변동\n"
            "- 지표 요약: SMA 교차, RSI 과매수/과매도, 볼린저 밴드 접촉 여부, 거래량 추세\n"
            "- 해석: 추세/모멘텀/변동성 관점의 시사점\n"
            "- 매수/매도 성향(권고 아님): 신중/보통/공격 중 하나 + 자신도(낮음/중간/높음)\n"
            "- 리스크 관리: 보수적 손절/익절 범위 예시(예: -3% / +6%), 시간지평(단기/중기), 논리가 무효화되는 조건\n"
            "- 면책: 실제 투자 결정은 사용자 책임이며, 추가 확인 필요\n"
            "허위 데이터 생성은 금지하며, 불확실하면 명시하세요."
        ),
    )
    
    @classmethod
    def validate(cls):
        """필수 환경변수 검증"""

        if cls.LLM_ID.startswith("openai:") and not cls.OPENAI_API_KEY:
            raise ValueError("OpenAI LLM 사용시 OPENAI_API_KEY 환경변수가 필요합니다.")
        
        return True 