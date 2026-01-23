#!/Users/jongsupbaek/stock_tracker/venv/bin/python
# -*- coding: utf-8 -*-
"""
네이버 금융에서 주식 정보를 가져오는 스크립트
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime, timedelta
import sys
import xml.etree.ElementTree as ET
import os


class NaverStockFetcher:
    def __init__(self):
        self.base_url = "https://finance.naver.com/item/main.nhn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # data 폴더: 스크립트 위치 기준으로 설정
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(script_dir, "data")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_stock_info(self, stock_code):
        """
        주식 정보를 가져옵니다.

        Args:
            stock_code (str): 종목 코드 (예: 005930 - 삼성전자)

        Returns:
            dict: 주식 정보 딕셔너리
        """
        try:
            url = f"{self.base_url}?code={stock_code}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 종목명 가져오기
            stock_name = soup.select_one('.wrap_company h2 a')
            stock_name = stock_name.text.strip() if stock_name else "알 수 없음"

            # 종가 (현재가)
            current_price = soup.select_one('.no_today .blind')
            current_price = current_price.text.strip() if current_price else "N/A"

            # 기본 정보
            stock_data = {
                "종목코드": stock_code,
                "종목명": stock_name,
                "날짜": datetime.now().strftime("%Y-%m-%d")
            }

            # 시가, 고가, 저가, 거래량 파싱 - new_totalinfo 영역에서 추출
            volume = None  # 거래량을 임시 저장
            totalinfo = soup.select_one('.new_totalinfo')
            if totalinfo:
                # 첫 번째 dl 안의 dd 요소들을 확인
                dd_elements = totalinfo.select('dl dd')

                for dd in dd_elements:
                    text = dd.get_text(strip=True)

                    # 각 항목별로 파싱 (전일가, 거래대금 제외)
                    if text.startswith('시가'):
                        stock_data['시가'] = text.replace('시가', '').strip().split()[0]
                    elif text.startswith('고가'):
                        stock_data['고가'] = text.replace('고가', '').strip().split()[0]
                    elif text.startswith('저가'):
                        stock_data['저가'] = text.replace('저가', '').strip().split()[0]
                    elif text.startswith('거래량'):
                        volume = text.replace('거래량', '').strip().split()[0]

            # 종가 추가 (시가, 고가, 저가 다음)
            stock_data['종가'] = current_price

            # 거래량을 마지막에 추가
            if volume:
                stock_data['거래량'] = volume

            return stock_data

        except requests.RequestException as e:
            print(f"네트워크 오류: {e}")
            return None
        except Exception as e:
            print(f"데이터 파싱 오류: {e}")
            return None

    def fetch_historical_data(self, stock_code, target_date=None, days=30):
        """
        과거 주식 정보를 가져옵니다.

        Args:
            stock_code (str): 종목 코드
            target_date (str): 조회할 날짜 (YYYY-MM-DD 형식), None이면 최근 데이터
            days (int): 가져올 일수 (기본 30일)

        Returns:
            dict or list: target_date가 지정되면 해당 날짜 데이터, 아니면 전체 리스트
        """
        try:
            url = f'https://fchart.stock.naver.com/sise.nhn?symbol={stock_code}&timeframe=day&count={days}&requestType=0'
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            # XML 파싱
            # EUC-KR 인코딩 처리
            content = response.content.decode('euc-kr')
            root = ET.fromstring(content)

            # 종목명 가져오기
            chartdata = root.find('chartdata')
            if chartdata is None:
                print("차트 데이터를 찾을 수 없습니다.")
                return None

            stock_name = chartdata.get('name', '알 수 없음')

            # 데이터 파싱
            items = chartdata.findall('item')
            historical_data = []

            for item in items:
                data_str = item.get('data')
                if not data_str:
                    continue

                # 형식: 날짜|시가|고가|저가|종가|거래량
                parts = data_str.split('|')
                if len(parts) >= 6:
                    date_str = parts[0]
                    # YYYYMMDD -> YYYY-MM-DD
                    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

                    stock_info = {
                        "종목코드": stock_code,
                        "종목명": stock_name,
                        "날짜": formatted_date,
                        "시가": parts[1],
                        "고가": parts[2],
                        "저가": parts[3],
                        "종가": parts[4],
                        "거래량": parts[5]
                    }
                    historical_data.append(stock_info)

            # 최신 데이터가 먼저 오므로 역순 정렬 (오래된 날짜부터)
            historical_data.reverse()

            # 특정 날짜 지정시 해당 날짜 데이터만 반환
            if target_date:
                for data in historical_data:
                    if data['날짜'] == target_date:
                        return data
                print(f"경고: {target_date}의 데이터를 찾을 수 없습니다. 주말이나 공휴일일 수 있습니다.")
                return None

            return historical_data

        except requests.RequestException as e:
            print(f"네트워크 오류: {e}")
            return None
        except ET.ParseError as e:
            print(f"XML 파싱 오류: {e}")
            return None
        except Exception as e:
            print(f"데이터 처리 오류: {e}")
            return None

    def calculate_moving_averages(self, data_list):
        """
        이동평균(MA5, MA10, MA20)을 계산하여 데이터에 추가

        Args:
            data_list: 날짜순으로 정렬된 데이터 리스트 (최신 날짜가 위)

        Returns:
            MA가 추가된 데이터 리스트
        """
        if not data_list or len(data_list) == 0:
            return data_list

        # 날짜 오름차순으로 정렬 (오래된 날짜부터)
        sorted_data = sorted(data_list, key=lambda x: x['날짜'])

        # 각 항목에 MA 계산
        for i, item in enumerate(sorted_data):
            # 종가를 숫자로 변환 (콤마 제거)
            close_prices = []
            for j in range(max(0, i - 19), i + 1):  # 최대 20일치 데이터
                close_str = sorted_data[j]['종가'].replace(',', '')
                close_prices.append(float(close_str))

            # MA5 계산
            if len(close_prices) >= 5:
                ma5 = sum(close_prices[-5:]) / 5
                item['MA5'] = f"{int(round(ma5)):,}원"
            else:
                item['MA5'] = "N/A"

            # MA10 계산
            if len(close_prices) >= 10:
                ma10 = sum(close_prices[-10:]) / 10
                item['MA10'] = f"{int(round(ma10)):,}원"
            else:
                item['MA10'] = "N/A"

            # MA20 계산
            if len(close_prices) >= 20:
                ma20 = sum(close_prices[-20:]) / 20
                item['MA20'] = f"{int(round(ma20)):,}원"
            else:
                item['MA20'] = "N/A"

        # 다시 최신 날짜 순으로 정렬
        sorted_data.reverse()
        return sorted_data

    def save_to_json(self, data, filename=None):
        """
        JSON 파일로 저장 (기존 파일에 날짜별로 append 및 정렬)

        Args:
            data: dict (단일 데이터) 또는 list (여러 데이터)
            filename: 파일명 (지정하지 않으면 종목코드 기반으로 자동 생성)
        """
        if not data:
            print("저장할 데이터가 없습니다.")
            return

        # data가 리스트인지 dict인지 확인
        is_list = isinstance(data, list)
        new_data_list = data if is_list else [data]

        if not new_data_list:
            print("저장할 데이터가 없습니다.")
            return

        # 종목코드 추출
        stock_code = new_data_list[0]['종목코드']

        if filename is None:
            filename = f"stock_{stock_code}.json"

        # data 폴더 안에 저장
        filepath = os.path.join(self.data_dir, filename)

        try:
            # 기존 파일이 있으면 읽기
            existing_data = []
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    # 단일 dict가 저장되어 있을 수도 있음
                    if isinstance(existing_data, dict):
                        existing_data = [existing_data]

            # 기존 데이터와 새 데이터 병합 (날짜를 키로 사용)
            data_dict = {}
            for item in existing_data:
                data_dict[item['날짜']] = item

            # 새 데이터로 업데이트 (같은 날짜면 덮어쓰기)
            for item in new_data_list:
                data_dict[item['날짜']] = item

            # 리스트로 변환 후 날짜 역순 정렬 (최신 날짜가 위)
            merged_data = sorted(data_dict.values(), key=lambda x: x['날짜'], reverse=True)

            # 이동평균 계산 (자르기 전에 먼저 계산)
            merged_data = self.calculate_moving_averages(merged_data)

            # 최근 20일 데이터만 유지 (MA 계산 후)
            merged_data = merged_data[:20]

            # 파일에 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)

            print(f"JSON 파일 저장 완료: {filepath} (총 {len(merged_data)}개 날짜)")
        except Exception as e:
            print(f"JSON 저장 오류: {e}")

    def save_to_csv(self, data, filename=None):
        """
        CSV 파일로 저장 (기존 파일에 날짜별로 append 및 정렬)

        Args:
            data: dict (단일 데이터) 또는 list (여러 데이터)
            filename: 파일명 (지정하지 않으면 종목코드 기반으로 자동 생성)
        """
        if not data:
            print("저장할 데이터가 없습니다.")
            return

        # data가 리스트인지 dict인지 확인
        is_list = isinstance(data, list)
        new_data_list = data if is_list else [data]

        if not new_data_list:
            print("저장할 데이터가 없습니다.")
            return

        # 종목코드 추출
        stock_code = new_data_list[0]['종목코드']

        if filename is None:
            filename = f"stock_{stock_code}.csv"

        # data 폴더 안에 저장
        filepath = os.path.join(self.data_dir, filename)

        try:
            # 기존 파일이 있으면 읽기
            existing_data = []
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8-sig', newline='') as f:
                    reader = csv.DictReader(f)
                    existing_data = list(reader)

            # 기존 데이터와 새 데이터 병합 (날짜를 키로 사용)
            data_dict = {}
            for item in existing_data:
                data_dict[item['날짜']] = item

            # 새 데이터로 업데이트 (같은 날짜면 덮어쓰기)
            for item in new_data_list:
                data_dict[item['날짜']] = item

            # 리스트로 변환 후 날짜 역순 정렬 (최신 날짜가 위)
            merged_data = sorted(data_dict.values(), key=lambda x: x['날짜'], reverse=True)

            # 이동평균 계산 (자르기 전에 먼저 계산)
            merged_data = self.calculate_moving_averages(merged_data)

            # 최근 20일 데이터만 유지 (MA 계산 후)
            merged_data = merged_data[:20]

            # 파일에 저장
            if merged_data:
                with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=merged_data[0].keys())
                    writer.writeheader()
                    writer.writerows(merged_data)

                print(f"CSV 파일 저장 완료: {filepath} (총 {len(merged_data)}개 날짜)")
        except Exception as e:
            print(f"CSV 저장 오류: {e}")


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python stock_fetcher.py <종목코드>                    # 현재가 조회")
        print("  python stock_fetcher.py <종목코드> --date YYYY-MM-DD  # 특정 날짜 조회")
        print("  python stock_fetcher.py <종목코드> --history [일수]   # 과거 데이터 조회 (기본 30일)")
        print("\n예시:")
        print("  python stock_fetcher.py 005930                        # 삼성전자 현재가")
        print("  python stock_fetcher.py 005930 --date 2024-12-31      # 2024년 12월 31일 데이터")
        print("  python stock_fetcher.py 005930 --history 10           # 최근 10일 데이터")
        print("\n주요 종목 코드:")
        print("  005930 - 삼성전자")
        print("  000660 - SK하이닉스")
        print("  035420 - NAVER")
        print("  005380 - 현대차")
        print("  051910 - LG화학")
        sys.exit(1)

    stock_code = sys.argv[1]
    fetcher = NaverStockFetcher()

    # 특정 날짜 조회
    if len(sys.argv) >= 4 and sys.argv[2] == '--date':
        target_date = sys.argv[3]
        print(f"종목 코드 {stock_code}의 {target_date} 정보를 가져오는 중...")

        stock_data = fetcher.fetch_historical_data(stock_code, target_date=target_date, days=100)

        if stock_data:
            # JSON과 CSV로 저장 (먼저 저장해야 MA가 계산됨)
            fetcher.save_to_json(stock_data)
            fetcher.save_to_csv(stock_data)

            # MA 정보와 함께 출력 (파일에서 읽어옴)
            filepath = os.path.join(fetcher.data_dir, f"stock_{stock_code}.json")
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    # 해당 날짜 데이터 찾기
                    target_data = None
                    for item in saved_data:
                        if item['날짜'] == target_date:
                            target_data = item
                            break

                    if target_data:
                        print("\n=== 주식 정보 ===")
                        for key, value in target_data.items():
                            print(f"{key}: {value}")
        else:
            print(f"{target_date}의 주식 정보를 가져오는데 실패했습니다.")
            print("주말이나 공휴일이 아닌지, 날짜 형식(YYYY-MM-DD)이 올바른지 확인해주세요.")
            sys.exit(1)

    # 과거 데이터 조회
    elif len(sys.argv) >= 3 and sys.argv[2] == '--history':
        days = int(sys.argv[3]) if len(sys.argv) >= 4 else 30
        print(f"종목 코드 {stock_code}의 최근 {days}일 데이터를 가져오는 중...")

        stock_data = fetcher.fetch_historical_data(stock_code, days=days)

        if stock_data and len(stock_data) > 0:
            # JSON과 CSV로 저장 (기존 파일에 병합, MA 계산 포함)
            fetcher.save_to_json(stock_data)
            fetcher.save_to_csv(stock_data)

            # MA 정보와 함께 출력 (파일에서 읽어옴)
            filepath = os.path.join(fetcher.data_dir, f"stock_{stock_code}.json")
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)

                    print(f"\n=== 최근 {len(saved_data)}일 주식 정보 (최근 10개) ===")
                    # 최신 10개만 출력
                    for data in saved_data[:10]:
                        ma_info = ""
                        if 'MA5' in data and data['MA5'] != 'N/A':
                            ma_info = f" | MA5: {data['MA5']}, MA10: {data['MA10']}, MA20: {data['MA20']}"
                        print(f"{data['날짜']}: 시가 {data['시가']}, 고가 {data['고가']}, 저가 {data['저가']}, 종가 {data['종가']}, 거래량 {data['거래량']}{ma_info}")

                    if len(saved_data) > 10:
                        print(f"... (총 {len(saved_data)}개 데이터)")
                    print()
        else:
            print("주식 정보를 가져오는데 실패했습니다.")
            sys.exit(1)

    # 현재가 조회 (기본)
    else:
        print(f"종목 코드 {stock_code}의 정보를 가져오는 중...")

        # 파일 존재 여부 확인 및 자동 초기화
        filepath = os.path.join(fetcher.data_dir, f"stock_{stock_code}.json")
        needs_init = False
        needs_gap_fill = False
        today_str = datetime.now().strftime("%Y-%m-%d")

        if not os.path.exists(filepath):
            needs_init = True
            print(f"\n새 종목입니다. 최근 20일(워킹데이) 데이터를 먼저 수집합니다...")
        else:
            # 기존 데이터 확인
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    if len(existing) < 20:
                        needs_init = True
                        print(f"\n기존 데이터({len(existing)}일)가 부족합니다. 20일 데이터를 수집합니다...")
                    elif existing[0]['날짜'] != today_str:
                        # 최신 데이터가 오늘이 아니면 gap이 있을 수 있음
                        needs_gap_fill = True
                        print(f"\n마지막 업데이트: {existing[0]['날짜']}")
                        print(f"누락된 데이터를 확인하기 위해 최근 10일 데이터를 수집합니다...")
            except:
                needs_init = True
                print(f"\n데이터 파일에 문제가 있습니다. 20일 데이터를 다시 수집합니다...")

        # 자동 초기화: 20 워킹데이 수집
        if needs_init:
            historical_data = fetcher.fetch_historical_data(stock_code, days=20)
            if historical_data:
                fetcher.save_to_json(historical_data)
                fetcher.save_to_csv(historical_data)
                print(f"초기 데이터 수집 완료 ({len(historical_data)}일)\n")
            else:
                print("경고: 과거 데이터 수집에 실패했습니다. 현재가만 조회합니다.\n")
        # Gap 메우기: 최근 10일 데이터를 가져와서 기존 데이터와 비교
        elif needs_gap_fill:
            historical_data = fetcher.fetch_historical_data(stock_code, days=10)
            if historical_data:
                # 기존 파일 읽기
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_dates = set(item['날짜'] for item in existing_data)

                # 새로운 날짜만 찾기
                new_dates = [item['날짜'] for item in historical_data if item['날짜'] not in existing_dates]

                if new_dates:
                    # 새로운 데이터가 있으면 병합
                    fetcher.save_to_json(historical_data)
                    fetcher.save_to_csv(historical_data)
                    print(f"누락 데이터 보완 완료: {len(new_dates)}일 추가됨\n")
                else:
                    # 새로운 데이터가 없으면 이미 최신 상태
                    print(f"데이터가 이미 최신 상태입니다.\n")

        stock_data = fetcher.fetch_stock_info(stock_code)

        if stock_data:
            print("\n=== 주식 정보 ===")
            for key, value in stock_data.items():
                print(f"{key}: {value}")

            # JSON과 CSV로 저장
            fetcher.save_to_json(stock_data)
            fetcher.save_to_csv(stock_data)

            # MA 정보 출력 (파일에서 읽어옴)
            filepath = os.path.join(fetcher.data_dir, f"stock_{stock_code}.json")
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    # 오늘 날짜 데이터 찾기
                    today_data = None
                    for item in saved_data:
                        if item['날짜'] == stock_data['날짜']:
                            today_data = item
                            break

                    if today_data and 'MA5' in today_data:
                        print(f"\n=== 이동평균 ===")
                        print(f"MA5: {today_data.get('MA5', 'N/A')}")
                        print(f"MA10: {today_data.get('MA10', 'N/A')}")
                        print(f"MA20: {today_data.get('MA20', 'N/A')}")
        else:
            print("주식 정보를 가져오는데 실패했습니다.")
            sys.exit(1)


if __name__ == "__main__":
    main()
