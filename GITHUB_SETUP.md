# GitHub에서 자동으로 주식 정보 수집하기

이 가이드는 GitHub Actions를 사용하여 클라우드에서 자동으로 주식 정보를 수집하는 방법을 설명합니다.

## 왜 GitHub Actions를 사용하나요?

- ✅ **클라우드 실행**: Mac을 켜두지 않아도 자동으로 실행됩니다
- ✅ **무료**: 공개 저장소는 완전 무료입니다
- ✅ **자동화**: 매일 정해진 시간에 자동으로 주식 데이터 수집
- ✅ **버전 관리**: 모든 데이터 변경 이력이 Git에 저장됩니다

## 설정 방법

### 1단계: GitHub 저장소 생성

1. [GitHub](https://github.com)에 로그인
2. 오른쪽 상단의 `+` → `New repository` 클릭
3. 저장소 이름: `stock_tracker`
4. **Public** 선택 (GitHub Actions 무료 사용을 위해)
5. `Create repository` 클릭

### 2단계: 로컬 코드를 GitHub에 푸시

```bash
cd ~/stock_tracker

# Git 초기화 (아직 안했다면)
git init

# 원격 저장소 연결 (YOUR_USERNAME을 본인 GitHub 아이디로 변경)
git remote add origin https://github.com/YOUR_USERNAME/stock_tracker.git

# 파일 추가 및 커밋
git add .
git commit -m "Initial commit: Stock tracker with GitHub Actions"

# GitHub에 푸시
git branch -M main
git push -u origin main
```

### 3단계: GitHub Actions 활성화

1. GitHub 저장소 페이지로 이동
2. `Actions` 탭 클릭
3. `I understand my workflows, go ahead and enable them` 클릭

### 4단계: 데이터 폴더 설정

GitHub Actions가 데이터를 저장하려면 `data/` 폴더가 필요합니다.

```bash
# data 폴더에 .gitkeep 파일 생성 (빈 폴더도 Git에 추가하기 위해)
touch ~/stock_tracker/data/.gitkeep

# .gitignore 수정 - data 폴더는 추적하되 내부 파일은 무시
```

[.gitignore](.gitignore) 파일을 다음과 같이 수정:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Virtual Environment
venv/
env/
ENV/

# Data files - JSON과 CSV만 제외, 폴더는 유지
data/*.json
data/*.csv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Environment variables
.env
.env.local
```

변경사항 커밋:

```bash
git add data/.gitkeep .gitignore
git commit -m "Add data folder and update .gitignore for GitHub Actions"
git push
```

## 사용 방법

### 자동 실행 (스케줄)

설정된 스케줄:
- **매일 오후 4시** (한국 시간 기준)
- **월요일~금요일만** (주말 제외)
- 자동으로 다음 종목 수집:
  - 005930 (삼성전자)
  - 000660 (SK하이닉스)
  - 035420 (NAVER)
  - 005380 (현대차)
  - 051910 (LG화학)

### 수동 실행

원할 때마다 수동으로 실행할 수 있습니다:

1. GitHub 저장소 페이지 → `Actions` 탭
2. 왼쪽에서 `주식 정보 자동 수집` 클릭
3. 오른쪽 `Run workflow` 버튼 클릭
4. (선택) 종목코드 입력 (예: `005930,000660,035420`)
5. `Run workflow` 클릭

### 실행 결과 확인

1. `Actions` 탭에서 워크플로우 실행 상태 확인
2. 완료되면 `data/` 폴더에 JSON, CSV 파일이 자동으로 업데이트됩니다
3. 커밋 메시지로 "📊 자동 주식 데이터 업데이트 - YYYY-MM-DD HH:MM:SS" 확인 가능

## 스케줄 변경하기

[.github/workflows/fetch_stocks.yml](.github/workflows/fetch_stocks.yml) 파일에서 cron 표현식을 수정:

```yaml
schedule:
  # 현재: 매일 오후 4시 (월-금)
  - cron: '0 7 * * 1-5'  # 7시 UTC = 한국 오후 4시
```

### Cron 표현식 예시

```yaml
# 매일 오전 9시 (한국 시간)
- cron: '0 0 * * *'    # 0시 UTC

# 매일 오전 9시, 오후 4시 (하루 2번)
- cron: '0 0,7 * * *'  # 0시, 7시 UTC

# 매주 월요일 오전 9시
- cron: '0 0 * * 1'    # 월요일 0시 UTC

# 매월 1일 오전 9시
- cron: '0 0 1 * *'    # 매월 1일 0시 UTC
```

## 수집 종목 변경하기

### 방법 1: 워크플로우 파일 수정

[.github/workflows/fetch_stocks.yml](.github/workflows/fetch_stocks.yml) 파일에서:

```yaml
- name: 주식 정보 수집
  run: |
    # 이 부분의 종목 리스트 수정
    STOCKS="005930,000660,035420,005380,051910"
```

### 방법 2: 수동 실행 시 지정

GitHub Actions 페이지에서 `Run workflow` 클릭 시 종목코드 입력

## 데이터 확인하기

### GitHub에서 직접 확인

1. 저장소의 `data/` 폴더로 이동
2. `stock_XXXXXX.json` 또는 `stock_XXXXXX.csv` 파일 클릭
3. GitHub 웹 인터페이스에서 바로 확인 가능

### 로컬로 다운로드

```bash
cd ~/stock_tracker
git pull
```

최신 데이터가 `data/` 폴더에 자동으로 다운로드됩니다.

## Claude Projects와 함께 사용하기

### Claude Projects에서 할 수 있는 것

1. **코드 개선**: "이동평균 계산 로직을 최적화해줘"
2. **기능 추가**: "RSI 지표를 추가해줘"
3. **버그 수정**: "특정 날짜 조회가 안돼. 디버깅해줘"
4. **리팩토링**: "코드를 더 깔끔하게 정리해줘"

### 워크플로우

```
1. Claude Projects에서 코드 개선/수정
   ↓
2. 수정된 코드를 로컬 Mac에 복사
   ↓
3. Git commit & push
   ↓
4. GitHub Actions가 자동으로 실행
```

## 문제 해결

### GitHub Actions가 실행되지 않음

1. `Actions` 탭에서 워크플로우가 활성화되어 있는지 확인
2. 저장소가 **Public**인지 확인 (Private은 무료 시간 제한 있음)
3. `.github/workflows/fetch_stocks.yml` 파일이 main 브랜치에 있는지 확인

### 데이터 파일이 업데이트되지 않음

1. Actions 탭에서 워크플로우 실행 로그 확인
2. 오류 메시지 확인
3. 네이버 금융 접속 제한이 있을 수 있음 (과도한 요청 시)

### Permission denied 오류

GitHub Actions가 저장소에 쓰기 권한이 필요합니다:

1. 저장소 Settings → Actions → General
2. "Workflow permissions" 섹션에서
3. ✅ "Read and write permissions" 선택
4. Save 클릭

## 비용

- **공개 저장소**: 완전 무료, 무제한
- **비공개 저장소**: 월 2,000분 무료 (개인 계정 기준)

이 프로젝트는 하루에 5~10분 정도만 사용하므로 비공개 저장소로 해도 무료 범위 내입니다.

## 다음 단계

이제 주식 정보가 자동으로 수집됩니다! 추가로:

1. **웹 대시보드** 만들기 - GitHub Pages로 시각화
2. **알림 기능** 추가 - 특정 가격 도달 시 이메일 발송
3. **API 서버** 구축 - 다른 앱에서 데이터 사용

더 자세한 내용은 [DEVELOPMENT.md](DEVELOPMENT.md)를 참고하세요.

## 참고 링크

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [Cron 표현식 생성기](https://crontab.guru/)
- [GitHub Actions 무료 사용량](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions)
