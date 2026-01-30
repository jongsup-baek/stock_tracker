#!/usr/bin/env python3
"""
US 주식 정보를 Yahoo Finance에서 수집하는 스크립트
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests


class YahooStockFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # data/us 폴더: 스크립트 위치 기준으로 설정 (미국 주식)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(script_dir, "data", "us")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_stock_info(self, ticker: str) -> dict | None:
        """
        Yahoo Finance에서 주식 정보를 가져옵니다.

        Args:
            ticker: 주식 티커 (예: AAPL, NVDA)

        Returns:
            주식 정보 딕셔너리 또는 None
        """
        try:
            # Yahoo Finance API 엔드포인트
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            params = {
                'range': '1mo',
                'interval': '1d',
                'includePrePost': 'false'
            }

            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
                print(f"Error: No data found for {ticker}")
                return None

            result = data['chart']['result'][0]
            meta = result['meta']
            timestamps = result['timestamp']
            indicators = result['indicators']['quote'][0]

            # 최근 거래일 데이터 추출
            stock_data = []
            for i in range(len(timestamps)):
                ts = timestamps[i]
                date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

                open_price = indicators['open'][i]
                high = indicators['high'][i]
                low = indicators['low'][i]
                close = indicators['close'][i]
                volume = indicators['volume'][i]

                if close is None:
                    continue

                stock_data.append({
                    'date': date,
                    'open': round(open_price, 2) if open_price else None,
                    'high': round(high, 2) if high else None,
                    'low': round(low, 2) if low else None,
                    'close': round(close, 2) if close else None,
                    'volume': volume
                })

            # MA 계산
            closes = [d['close'] for d in stock_data if d['close'] is not None]
            volumes = [d['volume'] for d in stock_data if d['volume'] is not None]

            for i, d in enumerate(stock_data):
                if d['close'] is None:
                    continue

                # 최신 데이터 기준으로 인덱스 계산 (stock_data는 오래된 순)
                idx = len(stock_data) - 1 - i
                recent_closes = closes[-(idx+1):] if idx + 1 <= len(closes) else closes

                # MA5
                if len(recent_closes) >= 5:
                    ma5 = sum(recent_closes[-5:]) / 5
                    d['MA5'] = round(ma5, 2)
                else:
                    d['MA5'] = None

                # MA10
                if len(recent_closes) >= 10:
                    ma10 = sum(recent_closes[-10:]) / 10
                    d['MA10'] = round(ma10, 2)
                else:
                    d['MA10'] = None

                # MA20
                if len(recent_closes) >= 20:
                    ma20 = sum(recent_closes[-20:]) / 20
                    d['MA20'] = round(ma20, 2)
                else:
                    d['MA20'] = None

            # 역순 정렬 (최신 데이터가 먼저)
            stock_data.reverse()

            # MA 재계산 (역순 정렬 후)
            closes_reversed = [d['close'] for d in reversed(stock_data) if d['close'] is not None]
            for i, d in enumerate(stock_data):
                if d['close'] is None:
                    continue

                # 현재 인덱스 기준으로 과거 데이터 추출
                # stock_data[0]이 최신, stock_data[-1]이 가장 오래됨
                # closes_reversed[0]이 가장 오래됨, closes_reversed[-1]이 최신
                # 현재 위치에서 과거 데이터만 사용해야 함
                end_idx = len(closes_reversed) - i
                recent_closes = closes_reversed[:end_idx]

                # MA5
                if len(recent_closes) >= 5:
                    ma5 = sum(recent_closes[-5:]) / 5
                    d['MA5'] = round(ma5, 2)
                else:
                    d['MA5'] = None

                # MA10
                if len(recent_closes) >= 10:
                    ma10 = sum(recent_closes[-10:]) / 10
                    d['MA10'] = round(ma10, 2)
                else:
                    d['MA10'] = None

                # MA20
                if len(recent_closes) >= 20:
                    ma20 = sum(recent_closes[-20:]) / 20
                    d['MA20'] = round(ma20, 2)
                else:
                    d['MA20'] = None

            return {
                'ticker': ticker,
                'name': meta.get('shortName', ticker),
                'currency': meta.get('currency', 'USD'),
                'data': stock_data
            }

        except requests.RequestException as e:
            print(f"Error fetching {ticker}: {e}")
            return None
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error parsing {ticker} data: {e}")
            return None

    def save_stock_data(self, ticker: str, stock_info: dict) -> bool:
        """
        주식 데이터를 JSON 파일로 저장합니다.

        Args:
            ticker: 주식 티커
            stock_info: 주식 정보 딕셔너리

        Returns:
            저장 성공 여부
        """
        if not stock_info or 'data' not in stock_info:
            return False

        file_path = os.path.join(self.data_dir, f"stock_{ticker}.json")

        # 기존 데이터 로드
        existing_data = []
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                existing_data = []

        # 기존 데이터를 날짜 기준으로 딕셔너리로 변환
        existing_by_date = {d['날짜']: d for d in existing_data}

        # 새 데이터 추가/업데이트
        for d in stock_info['data']:
            if d['close'] is None:
                continue

            record = {
                '티커': ticker,
                '종목명': stock_info['name'],
                '날짜': d['date'],
                '시가': d['open'],
                '고가': d['high'],
                '저가': d['low'],
                '종가': d['close'],
                '거래량': d['volume'],
                'MA5': d.get('MA5'),
                'MA10': d.get('MA10'),
                'MA20': d.get('MA20')
            }
            existing_by_date[d['date']] = record

        # 날짜 기준 정렬 (최신순)
        sorted_data = sorted(existing_by_date.values(), key=lambda x: x['날짜'], reverse=True)

        # 최근 20개만 유지
        sorted_data = sorted_data[:20]

        # JSON 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sorted_data, f, ensure_ascii=False, indent=2)

        print(f"Saved {ticker} data to {file_path}")
        return True


def extract_us_watchlist(portfolio_path: str = "docs/us/PORTFOLIO_US.md") -> list[str]:
    """
    PORTFOLIO_US.md에서 관심 종목 티커를 추출합니다.

    Returns:
        티커 리스트 (예: ['AAPL', 'NVDA', ...])
    """
    import re

    path = Path(portfolio_path)
    if not path.exists():
        # 스크립트 위치 기준으로 시도
        script_dir = Path(__file__).parent
        path = script_dir / portfolio_path

    if not path.exists():
        print(f"Error: {portfolio_path} not found", file=sys.stderr)
        return []

    content = path.read_text(encoding='utf-8')

    # "관심 종목 (Watchlist)" 섹션 찾기
    watchlist_section = re.search(
        r'## 관심 종목 \(Watchlist\).*?\n\n(.*?)(?=\n---|\n##|\Z)',
        content,
        re.DOTALL
    )

    if not watchlist_section:
        print("Error: Watchlist section not found", file=sys.stderr)
        return []

    watchlist_content = watchlist_section.group(1)

    # 테이블에서 티커 추출 (대문자 알파벳으로 구성된 티커)
    # | 종목명 | 티커 | 형식에서 티커 컬럼 추출
    tickers = re.findall(r'\|\s*([A-Z]+)\s*\|?\s*$', watchlist_content, re.MULTILINE)

    return tickers


def main():
    if len(sys.argv) < 2:
        # 인수 없으면 PORTFOLIO_US.md에서 읽기
        tickers = extract_us_watchlist()
        if not tickers:
            print("No tickers found. Please provide ticker as argument or check PORTFOLIO_US.md")
            sys.exit(1)
    else:
        tickers = [sys.argv[1].upper()]

    fetcher = YahooStockFetcher()

    for ticker in tickers:
        print(f"\nFetching {ticker}...")
        stock_info = fetcher.fetch_stock_info(ticker)

        if stock_info:
            fetcher.save_stock_data(ticker, stock_info)

            # 최신 데이터 출력
            if stock_info['data']:
                latest = stock_info['data'][0]
                print(f"  {stock_info['name']} ({ticker})")
                print(f"  Date: {latest['date']}")
                print(f"  Close: ${latest['close']}")
                print(f"  MA5: {latest.get('MA5', 'N/A')}")
                print(f"  MA10: {latest.get('MA10', 'N/A')}")
                print(f"  MA20: {latest.get('MA20', 'N/A')}")
        else:
            print(f"Failed to fetch {ticker}")


if __name__ == "__main__":
    main()
