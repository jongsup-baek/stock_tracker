# 네이버 주식 정보 수집기

네이버 금융에서 주식 정보를 가져와 JSON 및 CSV 파일로 저장하는 CLI 도구입니다.

## 주요 기능

- 실시간 현재가 조회
- 특정 날짜의 주식 정보 조회
- 과거 데이터 (일봉) 조회
- 이동평균(MA5, MA10, MA20) 자동 계산
- JSON 및 CSV 파일로 데이터 저장
- 자동 데이터 갭 감지 및 보완
- **GitHub Actions를 통한 클라우드 자동 실행** 🆕

## 빠른 시작

### 사용 방법

```bash
# 현재가 조회
stock 005930

# 특정 날짜 조회
stock 005930 --date 2026-01-20

# 과거 데이터 조회
stock 005930 --history 10
```

### 주요 종목 코드

| 종목명 | 코드 |
|--------|------|
| 삼성전자 | 005930 |
| SK하이닉스 | 000660 |
| NAVER | 035420 |
| 현대차 | 005380 |
| LG화학 | 051910 |
| POSCO홀딩스 | 005490 |

## 출력 예시

```
종목 코드 005930의 정보를 가져오는 중...

새 종목입니다. 최근 20일(워킹데이) 데이터를 먼저 수집합니다...
초기 데이터 수집 완료 (20일)

=== 주식 정보 ===
종목코드: 005930
종목명: 삼성전자
날짜: 2026-01-23
시가: 154,700
고가: 156,000
저가: 150,100
종가: 152,100
거래량: 25,195,543

=== 이동평균 ===
MA5: 149,680원
MA10: 145,790원
MA20: 137,485원
```

## 자동 데이터 관리

- **신규 종목**: 처음 조회 시 자동으로 최근 20일(워킹데이) 데이터 수집
- **누락 데이터 보완**: 마지막 업데이트가 오늘이 아닌 경우, 자동으로 누락된 날짜 데이터 추가
- **일상 업데이트**: 최신 상태이면 현재가만 빠르게 조회

## 출력 파일

조회 결과는 `~/stock_tracker/data/` 폴더에 자동 저장됩니다.

- `stock_005930.json` - JSON 형식
- `stock_005930.csv` - CSV 형식
- 최근 20일(워킹데이) 데이터만 유지

## 클라우드에서 자동 실행하기 🆕

Mac을 켜두지 않아도 GitHub Actions를 사용하여 클라우드에서 자동으로 주식 정보를 수집할 수 있습니다.

- 매일 정해진 시간에 자동 실행
- 무료로 사용 가능 (공개 저장소)
- 수동 실행도 가능

자세한 설정 방법은 [GITHUB_SETUP.md](GITHUB_SETUP.md)를 참고하세요.

## 투자 운영 문서 📁

`docs/` 폴더에 투자 운영을 위한 문서들이 있습니다.

| 문서 | 설명 |
|------|------|
| [OPERATION_MANUAL.md](docs/OPERATION_MANUAL.md) | 투자 규칙과 매매 조건 (v1.4) |
| [OPERATION_GUIDE.md](docs/OPERATION_GUIDE.md) | Daily Report 템플릿과 사용 가이드 |
| [PORTFOLIO.md](docs/PORTFOLIO.md) | 관심 종목 (Watchlist) |

### 일일 워크플로우 ⭐

Daily Report를 생성하기 위한 순서입니다:

```
1. GitHub Actions 실행 (수동 또는 자동)
   → Repository > Actions > "Daily Stock Data Update" > Run workflow

2. 로컬에 최신 데이터 동기화
   → cd ~/stock_tracker && git pull

3. Cowork 세션 시작
   → Claude Desktop에서 Cowork 모드로 stock_tracker 폴더 선택

4. Daily Report 요청
   → "1월 27일 Daily Report 만들어줘"
```

Claude가 자동으로:
- GitHub(로컬)에서 최신 주식 데이터 읽기
- GitHub에서 운영 매뉴얼 및 관심 종목 읽기
- Notion에서 매매 히스토리 읽기 (페이지 형식)
- 매수/매도 조건 점검 및 포트폴리오 분석
- Notion DB에 Daily Report 생성

### Notion 기록 규칙

| 항목 | 규칙 |
|------|------|
| **Daily Report Name** | "2026년 1월 26일" (날짜만) |
| **매매 히스토리** | 페이지 형식 (DB 아님), 날짜별 섹션으로 기록 |
| **미체결 주문** | 해당 날짜 섹션에 "종목명 매수 미체결"로 기록 |

### 트러블슈팅

| 문제 | 해결 |
|------|------|
| 주가 데이터가 오래됨 | GitHub Actions 수동 실행 후 `git pull` |
| Cowork에서 데이터 못 읽음 | stock_tracker 폴더 다시 선택 |
| 매매 히스토리 DB 읽기 실패 | 페이지 형식으로 변경됨 (2026-01-26~) |

## 처음 설치하는 경우

설치가 필요한 경우 [DEVELOPMENT.md](DEVELOPMENT.md) 문서를 참고하세요.

간단 설치 명령어:

```bash
cd ~/stock_tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x ~/stock_tracker/stock_fetcher.py
echo "alias stock='/Users/jongsupbaek/stock_tracker/stock_fetcher.py'" >> ~/.zshrc
source ~/.zshrc
```

## 문제 해결

### 'stock' 명령어를 찾을 수 없음

별칭이 설정되지 않았습니다. 다음 명령어를 실행하세요:

```bash
echo "alias stock='/Users/jongsupbaek/stock_tracker/stock_fetcher.py'" >> ~/.zshrc
source ~/.zshrc
```

### ModuleNotFoundError

패키지가 설치되지 않았습니다:

```bash
cd ~/stock_tracker
source venv/bin/activate
pip install -r requirements.txt
```

## 참고사항

- 네이버 금융의 이용약관을 준수하여 사용하세요
- 과도한 요청은 IP 차단의 원인이 될 수 있습니다
- 주말이나 공휴일의 데이터는 조회되지 않습니다

## 개발자 정보

코드 수정이나 개발에 참여하려면 [DEVELOPMENT.md](DEVELOPMENT.md) 문서를 참고하세요.

## 라이센스

이 프로젝트는 교육 목적으로 작성되었습니다.
