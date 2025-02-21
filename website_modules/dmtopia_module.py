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
    """도매토피아 로그인 수행 (프로필 이름 추가)"""
    try:
        driver.get(site_info["login_url"])
        print(f"[{profile_name}] 도매토피아 로그인 페이지 이동: {site_info['login_url']}")

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
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#doto_scrollmenu > div > div.menu_box_r > div > a"))
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

        print(f"✅ [{profile_name}] 도매토피아 로그인 성공!")
        return True

    except Exception as e:
        print(f"❌ [{profile_name}] 도매토피아 로그인 중 오류 발생: {e}")
        return False


def logout(driver, site_info, profile_name):
    """도매토피아 로그아웃 수행 (프로필 이름 추가)"""
    try:
        print(f"\n[{profile_name}] 🚪 도매토피아 로그아웃 시도...")
        # 로그아웃 버튼 클릭
        logout_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#doto_scrollmenu > div > div.menu_box_r > div > a"))
        )
        logout_button.click()
        time.sleep(2)  # 로그아웃 후 대기
        print(f"✅ [{profile_name}] 도매토피아 로그아웃 성공!")
        return True
    except Exception as e:
        print(f"❌ [{profile_name}] 도매토피아 로그아웃 중 오류 발생: {e}")
        return False


def navigate_to_order_details(driver, site_info, profile_name, collected_data):
    """도매토피아 주문배송조회 페이지 이동 → 주문번호 목록 클릭 → 상세 페이지에서 정보 수집 (최근 3일 주문만) (프로필 이름 추가)"""
    try:
        print(f"\n[{profile_name}] 도매토피아 주문배송조회 페이지 이동...")
        driver.get("https://www.dometopia.com/mypage/order_catalog")
        time.sleep(3)  # 페이지 로딩 대기

        print(f"✅ [{profile_name}] 도매토피아 주문배송조회 페이지 이동 완료!")

        # 주문번호 목록 가져오기
        order_numbers = driver.find_elements(By.CSS_SELECTOR,
            "#mypage-order_catalog > div.doto-table-wrap > table > tbody > tr > td.order-number > a > strong")

        if not order_numbers:
            print(f"[{profile_name}] ⚠️ 도매토피아 주문번호를 찾을 수 없음!")
            return False

        print(f"\n✅ [{profile_name}] 도매토피아 수집된 주문번호 목록:")
        for idx, order in enumerate(order_numbers, 1):
            print(f"[{profile_name}] {idx}. {order.text}")

        # 오늘 날짜와 3일 전 날짜 계산
        today = datetime.today()
        two_days_ago = today - timedelta(days=1)  # 오늘 포함 3일간이므로 2일 전까지
        today_str = today.strftime("%Y%m%d")
        yesterday_str = (today - timedelta(days=1)).strftime("%Y%m%d")
        #day_before_yesterday_str = two_days_ago.strftime("%Y%m%d")

        recent_days = [today_str, yesterday_str]
        #recent_days = [today_str] # 오늘만 수집하도록 변경
        print(f"\n🔎 [{profile_name}] 도매토피아 최근 2일({recent_days}) 주문번호만 수집합니다.")

        # 모든 주문번호에 대해 상세 페이지로 이동하여 정보 수집 (최근 3일 주문만)
        for idx in range(len(order_numbers)):
            order_number_text = order_numbers[idx].text
            order_date_prefix = order_number_text[:8] # 주문번호 앞 8자리가 날짜 (YYYYMMDD)

            if order_date_prefix in recent_days:
                print(f"\n🔗 [{profile_name}] 도매토피아 {order_number_text} (최근 2일 주문) 클릭하여 상세 페이지로 이동...")
                order_numbers[idx].click()
                time.sleep(3)  # 이동 후 대기

                print(f"✅ [{profile_name}] 도매토피아 주문 상세 페이지 이동 완료!")
                print(f"[{profile_name}] 현재 URL:", driver.current_url)

                # 상세 페이지에서 정보 수집 및 collected_data에 저장
                order_detail = extract_order_details(driver, site_info, profile_name) # 🚩 변경: 반환값 받기
                if order_detail: # 🚩 None이 아닐 경우만 추가
                    collected_data.append(order_detail) # 수집된 정보 리스트에 추가

                # 뒤로가기 (주문번호 목록으로 돌아가기)
                driver.back()
                time.sleep(3)  # 목록 페이지 로딩 대기

                # 뒤로 간 후 새로 주문번호 목록을 찾아 다시 클릭할 수 있도록 요소 갱신
                order_numbers = WebDriverWait(driver, 1).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                        "#mypage-order_catalog > div.doto-table-wrap > table > tbody > tr > td.order-number > a > strong"))
                )
                print(f"⚡ [{profile_name}] 도매토피아 새로운 주문번호 목록 갱신 완료!")
            else:
                print(f"\n🚫 [{profile_name}] 도매토피아 {order_number_text} (오래된 주문)는 최근 2일 주문이 아니므로 건너뜁니다.")
                continue # 최근 3일 주문이 아니면 건너뛴다

        return True

    except Exception as e:
        print(f"❌ [{profile_name}] 도매토피아 주문 상세 페이지 이동 중 오류 발생: {e}")
        return False


def extract_order_details(driver, site_info, profile_name):
    """도매토피아 주문 상세 페이지에서 배송번호, 배송사, 받는 사람 이름 수집 + 아이디 정보 추가 (프로필 이름 추가)"""
    try:
        print(f"\n📦 [{profile_name}] 도매토피아 주문 상세 정보 수집 시작...")

        # 아이디
        user_id = site_info["id"]

        # 배송번호
        try:
            delivery_number = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, site_info["delivery_number_selector"]))
            ).text
        except:
            delivery_number = "정보 없음"

        # 배송사와 배송정보 분리
        try:
            delivery_company_info = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, site_info["delivery_company_selector"]))
            ).text
            # 배송사와 배송정보 분리 (한진택배 458579242553에서 한진택배만 추출)
            delivery_company = delivery_company_info.split()[0]  # 첫 번째 단어(배송사)만 추출
            delivery_info = " ".join(delivery_company_info.split()[1:])  # 나머지는 배송정보로 처리
        except:
            delivery_company = "정보 없음"
            delivery_info = "정보 없음"

        # 받는 사람 이름에서 '님'과 불필요한 정보를 제거
        try:
            recipient_name = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, site_info["name_selector"]))
            ).text
            recipient_name = recipient_name.replace("님에게", "")  # "님" 제거
            recipient_name = recipient_name.split(" ")[0]  # 이름만 추출 (공백 이후 제거)
        except:
            recipient_name = "정보 없음"

        print("\n✅ [{profile_name}] 도매토피아 수집된 주문 상세 정보:")
        print(f"👤 [{profile_name}] 아이디: {user_id}") # 아이디 정보 추가 및 프로필 이름 추가
        print(f"🚚 [{profile_name}] 배송사: {delivery_company}")
        print(f"📦 [{profile_name}] 배송정보: {delivery_info}")
        print(f"👤 [{profile_name}] 받는 사람: {recipient_name}")

        # 🚩 수집된 정보를 딕셔너리 형태로 반환
        return {
            "site_name": site_info["site_name"], # 🚩 공급사 이름 추가
            "아이디": user_id,
            "배송사": delivery_company,
            "배송정보": delivery_info,
            "받는 사람": recipient_name
        }

    except Exception as e:
        print(f"❌ [{profile_name}] 도매토피아 주문 상세 정보 수집 중 오류 발생: {e}")
        return None # 🚩 오류 발생 시 None 반환