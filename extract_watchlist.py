#!/usr/bin/env python3
"""
PORTFOLIO.md에서 관심 종목 코드를 추출하는 스크립트
"""
import re
import sys
from pathlib import Path


def extract_stock_codes(portfolio_path: str = "docs/PORTFOLIO.md") -> list[str]:
    """
    PORTFOLIO.md에서 관심 종목 코드를 추출합니다.

    Returns:
        종목 코드 리스트 (예: ['005930', '000660', ...])
    """
    path = Path(portfolio_path)
    if not path.exists():
        print(f"Error: {portfolio_path} not found", file=sys.stderr)
        return []

    content = path.read_text(encoding='utf-8')

    # "관심 종목 (Watchlist)" 섹션 찾기
    watchlist_section = re.search(
        r'## 관심 종목 \(Watchlist\).*?\n\n(.*?)(?=\n##|\Z)',
        content,
        re.DOTALL
    )

    if not watchlist_section:
        print("Error: Watchlist section not found", file=sys.stderr)
        return []

    watchlist_content = watchlist_section.group(1)

    # 테이블에서 종목 코드 추출 (6자리 숫자)
    stock_codes = re.findall(r'\|\s*(\d{6})\s*\|', watchlist_content)

    return stock_codes


if __name__ == "__main__":
    codes = extract_stock_codes()

    if codes:
        # 쉼표로 구분된 종목 코드 출력 (GitHub Actions에서 사용)
        print(','.join(codes))
    else:
        sys.exit(1)
