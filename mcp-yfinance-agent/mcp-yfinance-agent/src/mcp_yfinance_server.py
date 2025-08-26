from __future__ import annotations
from typing import List, Dict
from dataclasses import asdict, dataclass
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import yfinance as yf
import time
from config import Config

mcp = FastMCP("YahooFinance")

class Quote(BaseModel):
    ticker: str
    price: float
    currency: str | None = None
    exchange: str | None = None

class Bar(BaseModel):
    datetime: str
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None

def safe_yf_call(func, *args, **kwargs):
    """안전한 Yahoo Finance API 호출"""
    for attempt in range(Config.YF_RETRY_COUNT):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == Config.YF_RETRY_COUNT - 1:
                raise e
            time.sleep(1)  # 재시도 전 잠시 대기

@mcp.tool()
def get_quote(ticker: str) -> Quote:
    """
    최신 가격/통화/거래소 정보를 조회합니다.
    """
    t = safe_yf_call(yf.Ticker, ticker)
    # fast_info가 환경마다 dict/객체 형태가 다를 수 있어 안전 접근
    fi = getattr(t, "fast_info", {}) or {}
    def gi(obj, key):
        return (obj.get(key) if isinstance(obj, dict) else getattr(obj, key, None))
    price = gi(fi, "last_price")
    currency = gi(fi, "currency") or gi(fi, "currency_code")
    exchange = gi(fi, "exchange")
    if price is None:
        # fallback: 최근 종가
        hist = safe_yf_call(t.history, period="1d", interval="1m")
        if not hist.empty:
            price = float(hist["Close"].iloc[-1])
    if price is None:
        raise RuntimeError(f"가격을 가져올 수 없습니다: {ticker}")
    return Quote(ticker=ticker.upper(), price=float(price), currency=currency, exchange=exchange)

@mcp.tool()
def get_history(
    ticker: str,
    period: str = "5d",
    interval: str = "1d",
    limit: int = 50
) -> List[Bar]:
    """
    히스토리 OHLCV를 반환합니다.
    period 예) 1d,5d,1mo,3mo,6mo,1y,5y,max
    interval 예) 1m,2m,5m,15m,30m,60m,90m,1d,1wk,1mo
    """
    df = safe_yf_call(yf.Ticker(ticker).history, period=period, interval=interval)
    if df.empty:
        return []
    # tail(limit)로 최근 N개만 반환
    df = df.tail(limit)
    rows: List[Bar] = []
    for idx, row in df.iterrows():
        rows.append(Bar(
            datetime=idx.to_pydatetime().isoformat(),
            open=float(row["Open"]),
            high=float(row["High"]),
            low=float(row["Low"]),
            close=float(row["Close"]),
            volume=(float(row["Volume"]) if "Volume" in row and row["Volume"] == row["Volume"] else None)
        ))
    return rows

if __name__ == "__main__":
    # 표준 입출력(stdio) 트랜스포트로 실행
    mcp.run(transport="stdio")
