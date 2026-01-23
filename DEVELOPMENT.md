# 개발자 가이드

이 문서는 프로젝트를 수정하거나 개발에 참여하려는 개발자를 위한 가이드입니다.

## 목차

- [개발 환경 설정](#개발-환경-설정)
- [프로젝트 구조](#프로젝트-구조)
- [코드 설명](#코드-설명)
- [데이터 구조](#데이터-구조)
- [테스트](#테스트)
- [배포](#배포)

## 개발 환경 설정

### 1. 가상환경 생성 및 활성화

```bash
cd ~/stock_tracker
python3 -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

**requirements.txt 내용:**
```
requests>=2.31.0       # HTTP 요청 라이브러리
beautifulsoup4>=4.12.0 # HTML 파싱 라이브러리
pandas>=2.0.0          # 데이터 분석 (선택사항)
lxml>=4.9.0            # XML/HTML 파서 (선택사항)
```

### 3. Python으로 직접 실행

```bash
python stock_fetcher.py 005930
```

### 4. 개발 시 유의사항

- 가상환경을 활성화한 상태에서 작업하세요
- 코드 수정 후 테스트할 때는 `python stock_fetcher.py` 명령어를 사용하세요
- 새 패키지를 추가한 경우 `pip freeze > requirements.txt`로 업데이트하세요

## 프로젝트 구조

```
stock_tracker/
├── stock_fetcher.py      # 메인 스크립트
├── requirements.txt      # 패키지 의존성
├── README.md            # 사용자 가이드
├── DEVELOPMENT.md       # 개발자 가이드 (이 파일)
├── venv/                # 가상환경 (git ignore)
└── data/                # 데이터 저장 폴더
    ├── stock_005930.json
    ├── stock_005930.csv
    └── ...
```

## 코드 설명

### 주요 클래스: NaverStockFetcher

```python
class NaverStockFetcher:
    def __init__(self):
        self.base_url = "https://finance.naver.com/item/main.nhn"
        self.headers = {'User-Agent': '...'}
        self.data_dir = os.path.join(script_dir, "data")
```

**주요 메서드:**

- `fetch_stock_info(stock_code)`: 현재가 조회
- `fetch_stock_info_by_date(stock_code, date)`: 특정 날짜 조회
- `fetch_historical_data(stock_code, days=30)`: 과거 데이터 조회
- `calculate_moving_averages(data)`: 이동평균 계산
- `save_to_json(data)`: JSON 파일 저장
- `save_to_csv(data)`: CSV 파일 저장

### 자동 초기화 로직

```python
# 파일이 없거나 데이터가 20일 미만이면 자동 초기화
if not os.path.exists(filepath) or len(existing) < 20:
    historical_data = fetcher.fetch_historical_data(stock_code, days=20)
    fetcher.save_to_json(historical_data)
    fetcher.save_to_csv(historical_data)
```

### Gap 감지 및 보완 로직

```python
# 마지막 업데이트가 오늘이 아니면 Gap이 있을 수 있음
elif existing[0]['날짜'] != today_str:
    historical_data = fetcher.fetch_historical_data(stock_code, days=10)
    new_dates = [item['날짜'] for item in historical_data
                 if item['날짜'] not in existing_dates]
    if new_dates:
        # 새로운 데이터 병합
```

## 데이터 구조

### JSON 파일 형식

```json
[
  {
    "종목코드": "005930",
    "종목명": "삼성전자",
    "날짜": "2026-01-23",
    "시가": "154700",
    "고가": "156000",
    "저가": "150100",
    "종가": "152100",
    "거래량": "25195543",
    "MA5": "149,680원",
    "MA10": "145,790원",
    "MA20": "137,485원"
  }
]
```

### CSV 파일 형식

```csv
종목코드,종목명,날짜,시가,고가,저가,종가,거래량,MA5,MA10,MA20
005930,삼성전자,2026-01-23,154700,156000,150100,152100,25195543,"149,680원","145,790원","137,485원"
```

### 데이터 저장 규칙

- 종목코드별로 하나의 파일에 **최근 20일(워킹데이)** 데이터만 저장
- 새로운 날짜를 조회하면 기존 파일에 자동으로 추가 (append)
- 같은 날짜를 다시 조회하면 최신 데이터로 업데이트
- 날짜는 최신순으로 자동 정렬 (가장 최근 날짜가 맨 위)
- 20일 이상 오래된 데이터는 자동으로 삭제

## 테스트

### 수동 테스트

```bash
# 가상환경 활성화
source venv/bin/activate

# 현재가 조회 테스트
python stock_fetcher.py 005930

# 특정 날짜 조회 테스트
python stock_fetcher.py 005930 --date 2026-01-20

# 과거 데이터 조회 테스트
python stock_fetcher.py 005930 --history 10
```

### 데이터 검증

1. `data/` 폴더에 파일이 생성되었는지 확인
2. JSON 파일이 올바른 형식인지 확인
3. CSV 파일이 Excel에서 열리는지 확인
4. 이동평균 계산이 정확한지 확인

### 예외 처리 테스트

```bash
# 존재하지 않는 종목코드
python stock_fetcher.py 999999

# 잘못된 날짜 형식
python stock_fetcher.py 005930 --date 20260120

# 주말/공휴일 날짜
python stock_fetcher.py 005930 --date 2026-01-25  # 토요일
```

## 일반 사용자를 위한 설치 스크립트

### 실행 가능하게 만들기

```bash
chmod +x ~/stock_tracker/stock_fetcher.py
```

### 쉘 별칭 설정

사용자의 쉘에 따라 다음 중 하나를 선택:

#### macOS 기본 쉘 (zsh)

```bash
echo "alias stock='/Users/jongsupbaek/stock_tracker/stock_fetcher.py'" >> ~/.zshrc
source ~/.zshrc
```

#### bash 쉘

```bash
echo "alias stock='/Users/jongsupbaek/stock_tracker/stock_fetcher.py'" >> ~/.bash_profile
source ~/.bash_profile
```

#### csh/tcsh 쉘

```bash
echo "alias stock '/Users/jongsupbaek/stock_tracker/stock_fetcher.py'" >> ~/.cshrc
source ~/.cshrc
```

### Shebang 라인 설명

파일 첫 줄의 `#!/Users/jongsupbaek/stock_tracker/venv/bin/python`은:
- 스크립트가 어떤 Python 인터프리터를 사용할지 지정
- 가상환경의 Python을 자동으로 사용하므로 venv 활성화 불필요
- 스크립트를 직접 실행 가능하게 만듦

## 배포

### 일반 사용자 배포

1. 프로젝트 폴더를 사용자의 홈 디렉토리에 복사
2. 가상환경 생성 및 패키지 설치
3. 실행 권한 부여 (`chmod +x`)
4. 쉘 별칭 설정

### Git 저장소 배포

```bash
# .gitignore 파일에 다음 추가
venv/
data/
*.pyc
__pycache__/
.DS_Store
```

## 에러 해결

### ModuleNotFoundError: No module named 'requests'

가상환경이 활성화되지 않았거나 패키지가 설치되지 않았습니다.

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### externally-managed-environment 오류

시스템 Python이 관리되는 환경입니다. 가상환경을 사용하세요:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 특정 날짜 데이터를 찾을 수 없음

다음을 확인하세요:
- 주말이나 공휴일인지 확인
- 날짜 형식이 `YYYY-MM-DD`인지 확인
- 너무 오래된 날짜는 조회되지 않을 수 있음 (최근 100일 이내 권장)

## 추가 개발 아이디어

### 기능 개선

- [ ] 여러 종목 동시 조회
- [ ] 데이터 시각화 (차트 생성)
- [ ] 알림 기능 (가격 도달 시 알림)
- [ ] 데이터베이스 연동 (SQLite, PostgreSQL)

### 웹 서비스 전환

1. **Backend API** (FastAPI, Flask)
   - REST API 엔드포인트 설계
   - 인증/권한 관리
   - 캐싱 전략

2. **Frontend** (React, Vue, HTML)
   - 검색 인터페이스
   - 차트 시각화
   - 실시간 업데이트

3. **배포** (Docker, AWS, Heroku)
   - 컨테이너화
   - CI/CD 파이프라인
   - 스케일링 전략

## 기여 가이드

프로젝트에 기여하려면:

1. Fork 저장소
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경 사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 연락처

프로젝트 관련 문의나 버그 리포트는 이슈 트래커를 이용해 주세요.

## 라이센스

이 프로젝트는 교육 목적으로 작성되었습니다.
