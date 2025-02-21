from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta

def set_headless_option(options):
    """ChromeOptions에 헤드리스 모드 설정 추가"""
    options.add_argument("--headless")  # 헤드리스 모드 활성화
    options.add_argument("--disable-gpu")  # GPU 가속 비활성화 (일부 환경에서 필요)
    return options


def login(driver, site_info, profile_name):
    """도매펫 로그인 수행 (프로필 이름 추가)"""
    try:
        driver.get(site_info["login_url"])
        print(f"[{profile_name}] 도매펫 로그인 페이지 이동: {site_info['login_url']}")

        # 알림창 처리 (로그인 페이지 접속 직후)
        try:
            alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
            if alert:
                alert_text = alert.text
                print(f"[{profile_name}] ⛔ 알림창 감지: {alert_text}")
                try:
                    alert.dismiss()
                    print(f"[{profile_name}] ✅ 알림창 dismiss() 완료 (취소)")
                except:
                    print(f"[{profile_name}] ⛔ dismiss() 실패, accept() 시도")
                    alert.accept()
                    print(f"[{profile_name}] ✅ 알림창 accept() 완료 (확인)")
                time.sleep(1)
        except:
            print(f"[{profile_name}] 알림창 감지 안됨 (정상)")

        # 로그아웃 먼저 시도
        try:
            logout_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#header > div.header_gnb > div > ul > li:nth-child(1) > a"))
            )
            logout_button.click()
            print(f"[{profile_name}] 로그아웃 성공: {site_info['site_name']}")
            time.sleep(2)  # 로그아웃 후 대기
        except:
            print(f"[{profile_name}] 이미 로그아웃 상태이거나 로그아웃 버튼을 찾을 수 없음.")

        # ID 입력
        id_input = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, site_info["id_selector"]))
        )
        id_input.clear()  # 🚩 기존 데이터 삭제 코드 추가
        id_input.send_keys(site_info["id"])

        # PW 입력
        pw_input = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, site_info["pw_selector"]))
        )
        pw_input.send_keys(site_info["pw"])

        # 로그인 버튼 클릭
        login_button = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, site_info["login_button_selector"]))
        )
        login_button.click()

        time.sleep(3)  # 로그인 후 페이지 로딩 대기

        print(f"✅ [{profile_name}] 도매펫 로그인 성공!")
        return True

    except Exception as e:
        print(f"❌ [{profile_name}] 도매펫 로그인 중 오류 발생: {e}")
        return False


def logout(driver, site_info, profile_name):
    """도매펫 로그아웃 수행 (프로필 이름 추가)"""
    try:
        print(f"\n[{profile_name}] 🚪 도매펫 로그아웃 시도...")
        # 로그아웃 버튼 클릭
        logout_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#header > div.header_gnb > div > ul > li:nth-child(1) > a"))
        )
        logout_button.click()
        time.sleep(2)  # 로그아웃 후 대기
        print(f"✅ [{profile_name}] 도매펫 로그아웃 성공!")
        return True
    except Exception as e:
        print(f"❌ [{profile_name}] 도매펫 로그아웃 중 오류 발생: {e}")
        return False


def navigate_to_order_details(driver, site_info, profile_name, collected_data):
    """도매펫 주문배송조회 페이지 이동 → 주문번호 목록에서 정보 수집 (상세 페이지 X) (프로필 이름 추가)"""
    try:
        print(f"\n[{profile_name}] 도매펫 주문배송조회 페이지 이동...")
        driver.get("https://www.domepet.com/mypage/order_list.php")  # ✅ 수정된 주문배송조회 페이지 URL
        time.sleep(3)  # 페이지 로딩 대기

        print(f"✅ [{profile_name}] 도매펫 주문배송조회 페이지 이동 완료!")

        # 주문 목록 테이블의 각 행(주문) 가져오기
        order_rows = driver.find_elements(By.CSS_SELECTOR,
            "#contents > div.sub_content > div.content > div > div.mypage_lately_info > div.mypage_lately_info_cont > div.mypage_table_type > table > tbody > tr") # ⚠️ 주문 목록 테이블 행 CSS selector (수정 필요할 수 있음)

        if not order_rows:
            print(f"[{profile_name}] ⚠️ 도매펫 주문 목록을 찾을 수 없음!")
            return False

        print(f"\n✅ [{profile_name}] 도매펫 주문 목록에서 정보 수집 시작:")

        # 오늘 날짜와 2일 전 날짜 계산 (최근 2일 주문 필터링 로직) ⚠️ 2일 전으로 수정
        today = datetime.today()
        two_days_ago = today - timedelta(days=1) # ⚠️ 2일 전으로 수정 (timedelta(days=1))
        today_str = today.strftime("%y%m%d") # ⚠️ YYMMDD 형식으로 변경
        yesterday_str = (today - timedelta(days=1)).strftime("%y%m%d") # ⚠️ YYMMDD 형식으로 변경
        #day_before_yesterday_str = three_days_ago.strftime("%y%m%d") # ⚠️ YYMMDD 형식으로 변경 - 이제 불필요
        #recent_days = [today_str, yesterday_str, day_before_yesterday_str] # ⚠️ 최근 3일 날짜 포함 - 수정
        recent_days = [today_str, yesterday_str] # ⚠️ 최근 2일 날짜 포함으로 수정
        #recent_days = [today_str] # 오늘만 수집하도록 변경 (조정 가능) - 이제 2일전으로
        print(f"\n🔎 [{profile_name}] 도매펫 최근 2일({recent_days}) 주문번호만 수집합니다. (현재는 모든 주문 수집)") # ⚠️ 메시지 수정: 최근 2일로 변경

        # 주문 목록 순회하며 정보 추출
        for row in order_rows:
            try:
                order_number_element = row.find_element(By.CSS_SELECTOR, "td.order_day_num > a > span") # ⚠️ 주문번호 CSS selector (수정 필요할 수 있음)
                order_number_text = order_number_element.text
                order_date_prefix = order_number_text[:6] # 주문번호 앞 6자리가 날짜 (YYMMDD)

                if order_date_prefix in recent_days: # 최근 2일 주문 필터링 (필요에 따라 활성화) ⚠️ 2일로 변경
                    print(f"\n📦 [{profile_name}] 주문번호: {order_number_text} 정보 수집...")

                    # 각 컬럼별 데이터 추출 (CSS selector 수정 필요)
                    delivery_company_info_element = row.find_element(By.CSS_SELECTOR, "td:nth-child(5)") # ⚠️ 배송사+정보 CSS selector (수정 필요)
                    delivery_company_info = delivery_company_info_element.text.strip() # 공백 제거

                    # 개선된 배송사와 배송정보 분리 로직
                    delivery_company = "정보 없음" # 기본값 설정
                    delivery_number = "정보 없음" # 기본값 설정
                    if delivery_company_info:
                        delivery_company_info = delivery_company_info.replace("배송준비 후 발송", "").replace("배송조회", "").strip() # "배송준비 후 발송", "배송조회" 제거
                        parts = delivery_company_info.split('(') # '(' 기준으로 분리
                        if len(parts) > 1:
                            delivery_company_part = parts[1].split(')') # ')' 기준으로 재분리
                            if len(delivery_company_part) > 0:
                                delivery_company = delivery_company_part[0].strip() # 괄호 안쪽 텍스트 추출 후 공백 제거
                        delivery_number_parts = delivery_company_info.split(')') # ')' 기준으로 분리
                        if len(delivery_number_parts) > 1:
                            delivery_number = delivery_number_parts[1].strip() # 배송번호 추출 및 공백 제거


                    recipient_name_element = row.find_element(By.CSS_SELECTOR, "td.order_day_num > b") # ⚠️ 받는 사람 이름 CSS selector (수정 필요)
                    recipient_name = recipient_name_element.text.strip() # 받는 사람 이름 추출 및 정제

                    # 수집된 정보 딕셔너리에 저장
                    order_detail = {
                        "site_name": site_info["site_name"], # 🚩 공급사 이름 추가
                        "아이디": site_info["id"],
                       # "주문번호": order_number_text,
                        "배송사": delivery_company,
                        "배송정보": delivery_number, # 배송번호를 배송정보로 사용
                        "받는 사람": recipient_name
                    }
                    collected_data.append(order_detail)
                    print(f"✅ [{profile_name}] 주문번호: {order_number_text} 정보 수집 완료")
                else:
                    print(f"\n🚫 [{profile_name}] {order_number_text} (오래된 주문)는 최근 2일 주문이 아니므로 건너뜁니다. (현재는 모든 주문 수집)") # ⚠️ 메시지 수정: 최근 2일로 변경, 필터링 로직 활성화 시 메시지 변경

            except Exception as row_e:
                print(f"❌ [{profile_name}] 주문 목록 행 처리 중 오류 발생: {row_e}")
                continue # 행 처리 중 오류 발생해도 다음 행 계속 처리

        return True

    except Exception as e:
        print(f"❌ [{profile_name}] 도매펫 주문 배송 조회 페이지 작업 중 오류 발생: {e}")
        return False


# extract_order_details 함수 삭제 (이전 버전에서 이미 삭제됨)

def logout(driver, site_info, profile_name):
    """도매펫 로그아웃 수행 (프로필 이름 추가)"""
    try:
        print(f"\n[{profile_name}] 🚪 도매펫 로그아웃 시도...")
        # 로그아웃 버튼 클릭
        logout_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#header > div.header_gnb > div > ul > li:nth-child(1) > a")) # ⚠️ 로그아웃 버튼 selector는 도매펫에 맞게 수정해야 할 수 있음
        )
        logout_button.click()
        time.sleep(2)  # 로그아웃 후 대기
        print(f"✅ [{profile_name}] 도매펫 로그아웃 성공!")
        return True
    except Exception as e:
        print(f"❌ [{profile_name}] 도매펫 로그아웃 중 오류 발생: {e}")
        return False

def set_headless_option(options):
    """ChromeOptions에 헤드리스 모드 설정 추가"""
    options.add_argument("--headless")  # 헤드리스 모드 활성화
    options.add_argument("--disable-gpu")  # GPU 가속 비활성화 (일부 환경에서 필요)
    return options