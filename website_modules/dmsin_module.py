from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from datetime import datetime, timedelta

def set_headless_option(options):
    """ChromeOptions에 헤드리스 모드 설정 추가"""
    options.add_argument("--headless")  # 헤드리스 모드 활성화
    options.add_argument("--disable-gpu")  # GPU 가속 비활성화 (일부 환경에서 필요)
    return options


def login(driver, site_info, profile_name):
    """도매신 로그인 수행 (프로필 이름 추가)"""
    try:
        driver.get(site_info["login_url"])
        print(f"[{profile_name}] 도매신 로그인 페이지 이동: {site_info['login_url']}")

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
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#header > div.part_01 > div > ul.JS_topMenu.menuOver > li:nth-child(1) > a"))
            )
            logout_button.click()
            print(f"[{profile_name}] 로그아웃 성공: {site_info['site_name']}")
            time.sleep(2)  # 로그아웃 후 대기
        except:
            print(f"[{profile_name}] 이미 로그아웃 상태이거나 로그아웃 버튼을 찾을 수 없음.")

        # ID 입력
        id_input = WebDriverWait(driver, 10).until(  # Wait up to 10 seconds
            EC.presence_of_element_located((By.CSS_SELECTOR, "#member_id"))
        )
        id_input.clear()  # 🚩 기존 데이터 삭제 코드 추가
        id_input.send_keys(site_info["id"])

        # PW 입력
        pw_input = WebDriverWait(driver, 10).until(  # Wait up to 10 seconds
            EC.presence_of_element_located((By.CSS_SELECTOR, "#member_passwd"))
        )
        pw_input.send_keys(site_info["pw"])

        # 로그인 버튼 클릭
        login_button = WebDriverWait(driver, 10).until(  # Wait up to 10 seconds
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.-btn.-block.-xl.-black"))
        )
        login_button.click()

        time.sleep(3)  # 로그인 후 페이지 로딩 대기

        print(f"✅ [{profile_name}] 도매신 로그인 성공!")
        return True

    except Exception as e:
        print(f"❌ [{profile_name}] 도매신 로그인 중 오류 발생: {e}")
        return False


def logout(driver, site_info, profile_name):
    """도매신 로그아웃 수행 (프로필 이름 추가)"""
    try:
        print(f"\n[{profile_name}] 🚪 도매신 로그아웃 시도...")
        # 로그아웃 버튼 클릭
        logout_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#header > div.part_01 > div > ul.JS_topMenu.menuOver > li:nth-child(1) > a"))
        )
        logout_button.click()
        time.sleep(2)  # 로그아웃 후 대기
        print(f"✅ [{profile_name}] 도매신 로그아웃 성공!")
        return True
    except Exception as e:
        print(f"❌ [{profile_name}] 도매신 로그아웃 중 오류 발생: {e}")
        return False
def navigate_to_order_details(driver, site_info, profile_name, collected_data):
    """도매신 주문배송조회 페이지 이동 → 주문번호 목록에서 정보 수집 (상세 페이지 X) (프로필 이름 추가)"""
    try:
        print(f"\n[{profile_name}] 도매신 주문배송조회 페이지 이동...")
        driver.get("https://domesin.co.kr/myshop/order/list.html")  # ✅ 수정된 주문배송조회 페이지 URL
        time.sleep(3)  # 페이지 로딩 대기

        print(f"✅ [{profile_name}] 도매신 주문배송조회 페이지 이동 완료!")

        # 주문 목록 테이블의 각 행(주문) 가져오기
        order_rows = driver.find_elements(By.CSS_SELECTOR,
           "#contents > div.xans-element-.xans-myshop.xans-myshop-orderhistorylistitem > div > div.ec-base-table.typeList > table > tbody > tr") # ⚠️ 주문 목록 테이블 행 CSS selector (수정 필요할 수 있음)


        if not order_rows or "검색된 내역이 없습니다" in driver.page_source:
            print(f"[{profile_name}] ⚠️ 도매신 주문 목록을 찾을 수 없음!")
            return False

        print(f"\n✅ [{profile_name}] 도매신 주문 목록에서 정보 수집 시작:")

        # 오늘 날짜와 2일 전 날짜 계산 (최근 2일 주문 필터링 로직) ⚠️ 2일 전으로 수정
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        today_str = today.strftime("%Y-%m-%d")  # YYYY-MM-DD 형식으로 변경
        yesterday_str = yesterday.strftime("%Y-%m-%d")  # YYYY-MM-DD 형식으로 변경

        recent_days = [today_str, yesterday_str]
        print(f"\n🔎 [{profile_name}] 도매신 최근 2일({recent_days}) 주문번호만 수집합니다.")

        # 주문 목록 순회하며 정보 추출
        for row in order_rows:
            try:
                # 주문번호 추출 (CSS Selector 수정)
                order_number_element = row.find_element(By.CSS_SELECTOR, "td:nth-child(1) > div > span.number > a")
                order_number_text = order_number_element.text.strip()
                order_date_prefix = order_number_text[:10]  # 주문번호 앞 10자리가 날짜 (YYYY-MM-DD)

                if order_date_prefix in recent_days:  # 최근 2일 주문 필터링
                    print(f"\n📦 [{profile_name}] 주문번호: {order_number_text} 정보 수집...")
                    order_detail_url = order_number_element.get_attribute("href")  # 주문 상세 페이지 URL 추출
                    driver.get(order_detail_url)
                    time.sleep(2)

                    # 받는 사람 이름 추출 (CSS Selector 수정)
                    recipient_name_element = driver.find_element(By.CSS_SELECTOR, "#contents > div > div.ec-base-fold.theme1.selected.eToggle > div.contents > div > table > tbody > tr:nth-child(2) > td")
                    recipient_name = recipient_name_element.text.strip()

                    # 배송 정보 추출 (CSS Selector 수정)
                    delivery_info_element = driver.find_element(By.CSS_SELECTOR, "#contents > div > div.ec-base-fold.theme1.selected.eToggle > div.contents > div > table > tbody > tr:nth-child(5) > td")
                    delivery_info_combined = delivery_info_element.text.strip()

                    delivery_company = "정보 없음"  # 기본값
                    delivery_number = "정보 없음"  # 기본값
                    parts = delivery_info_combined.split("I")
                    if len(parts) == 2:
                        delivery_company = parts[0].strip()
                        delivery_number = parts[1].strip()
                        print(f"✅ [{profile_name}] 택배사: {delivery_company}, 송장번호: {delivery_number}")
                    else:
                        print(f"⚠️ [{profile_name}] 택배사/송장번호 추출 실패: {delivery_info_combined}")

                    # 수집된 정보 딕셔너리에 저장
                    order_detail = {
                        "site_name": site_info["site_name"],  # 🚩 공급사 이름 추가
                        "아이디": site_info["id"],
                        "주문번호": order_number_text,
                        "배송사": delivery_company,
                        "배송정보": delivery_number,  # 배송번호를 배송정보로 사용
                        "받는 사람": recipient_name
                    }
                    collected_data.append(order_detail)
                    print(f"✅ [{profile_name}] 주문번호: {order_number_text} 정보 수집 완료")

                else:
                    print(f"\n🚫 [{profile_name}] {order_number_text} (오래된 주문)는 최근 2일 주문이 아니므로 건너뜁니다.")

            except Exception as row_e:
                print(f"❌ [{profile_name}] 주문 목록 행 처리 중 오류 발생: {row_e}")
                continue  # 행 처리 중 오류 발생해도 다음 행 계속 처리

        return True

    except Exception as e:
        print(f"❌ [{profile_name}] 도매신 주문 배송 조회 페이지 작업 중 오류 발생: {e}")
        return False

def set_headless_option(options):
    """ChromeOptions에 헤드리스 모드 설정 추가"""
    options.add_argument("--headless")  # 헤드리스 모드 활성화
    options.add_argument("--disable-gpu")  # GPU 가속 비활성화 (일부 환경에서 필요)
    return options