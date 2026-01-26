# 네이버 주식 정보 수집기

네이버 금융에서 주식 정보를 가져와 JSON 및 CSV 파일로 저장하고, Claude와 함께 Daily Report를 생성하는 도구입니다.

---

## 목차

1. [Daily Report 생성 워크플로우](#1-daily-report-생성-워크플로우-)
2. [Claude에게 요청할 수 있는 것들](#2-claude에게-요청할-수-있는-것들)
3. [Notion 기록 규칙](#3-notion-기록-규칙)
4. [워크플로우 트러블슈팅](#4-워크플로우-트러블슈팅)
5. [투자 운영 문서](#5-투자-운영-문서-)
6. [CLI 도구 및 개발자 문서](#6-cli-도구-및-개발자-문서-)

---

## 1. Daily Report 생성 워크플로우 ⭐

Daily Report를 생성하기 위한 순서입니다:

```
1. GitHub Actions 실행 (수동 또는 자동)
   → Repository > Actions > "주식 정보 자동 수집" > Run workflow

2. 로컬에 최신 데이터 동기화
   → cd ~/jongsup-baek.github/stock_tracker && git pull

3. Cowork 세션 시작
   → Claude Desktop에서 Cowork 모드로 stock_tracker 폴더 선택

4. Notion 페이지 링크 공유 및 숙지 요청
   → "https://www.notion.so/2c0ef155d17180c99ff9c7d243962092 확인해줘"
   → "README 잘 읽고, Notion 페이지 꼼꼼히 읽고, 작업 어떻게 해야 할지 숙지해"

5. Daily Report 요청
   → "1월 27일 Daily Report 만들어줘"
```

Claude가 자동으로:
- GitHub(로컬)에서 최신 주식 데이터 읽기
- GitHub에서 운영 매뉴얼 및 관심 종목 읽기
- Notion에서 매매 히스토리 읽기 (페이지 형식)
- 매수/매도 조건 점검 및 포트폴리오 분석
- Notion DB에 Daily Report 생성

---

## 2. Claude에게 요청할 수 있는 것들

| 요청 | 예시 |
|------|------|
| Daily Report 생성 | "1월 27일 Daily Report 만들어줘" |
| 매매 기록 | "오늘 삼성전자 10주 매수했어" |
| 미체결 기록 | "현대모비스 매수 미체결됐어" |
| 매도 기록 | "SK하이닉스 전량 매도했어 (익절)" |
| 종목 분석 | "삼성전자 매수 조건 확인해줘" |
| 포트폴리오 현황 | "현재 보유 종목 수익률 알려줘" |

---

## 3. Notion 기록 규칙

| 항목 | 규칙 |
|------|------|
| **Daily Report Name** | "2026년 1월 26일" (날짜만) |
| **매매 히스토리** | 페이지 형식 (DB 아님), 날짜별 섹션으로 기록 |
| **미체결 주문** | 해당 날짜 섹션에 "종목명 매수 미체결"로 기록 |

---

## 4. 워크플로우 트러블슈팅

| 문제 | 해결 |
|------|------|
| 주가 데이터가 오래됨 | GitHub Actions 수동 실행 후 `git pull` |
| Cowork에서 데이터 못 읽음 | stock_tracker 폴더 다시 선택 |
| 매매 히스토리 DB 읽기 실패 | 페이지 형식으로 변경됨 (2026-01-26~) |
| GitHub Actions 자동 실행 안됨 | Actions 탭에서 워크플로우 활성화 확인 |

---

## 5. 투자 운영 문서 📁

`docs/` 폴더에 투자 운영을 위한 문서들이 있습니다.

| 문서 | 설명 |
|------|------|
| [OPERATION_MANUAL.md](docs/OPERATION_MANUAL.md) | 투자 규칙과 매매 조건 (v1.4) |
| [OPERATION_GUIDE.md](docs/OPERATION_GUIDE.md) | Daily Report 템플릿과 사용 가이드 |
| [PORTFOLIO.md](docs/PORTFOLIO.md) | 관심 종목 (Watchlist) |

---

## 6. CLI 도구 및 개발자 문서 📁

stock_fetcher.py CLI 사용법, 설치 방법, 개발 가이드는 아래 문서를 참고하세요.

| 문서 | 설명 |
|------|------|
| [DEVELOPMENT.md](DEVELOPMENT.md) | CLI 사용법, 설치, 개발자 가이드 |
| [GITHUB_SETUP.md](GITHUB_SETUP.md) | GitHub Actions 설정 방법 |

---

## 라이센스

이 프로젝트는 교육 목적으로 작성되었습니다.
