from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from datetime import datetime, timedelta
from selenium.common.exceptions import NoAlertPresentException, TimeoutException

def set_headless_option(options):
    """ChromeOptions에 헤드리스 모드 설정 추가"""
    options.add_argument("--headless")  # 헤드리스 모드 활성화
    options.add_argument("--disable-gpu")  # GPU 가속 비활성화 (일부 환경에서 필요)
    return options


def login(driver, site_info, profile_name):
    """도매직방 로그인 수행 (프로필 이름 추가)"""
    
    try:
        driver.get(site_info["login_url"])
        
        # 알림창 처리 (로그인 페이지 접속 직후)
        try:
            alert = WebDriverWait(driver, 1).until(EC.alert_is_present()) # Increased timeout to 10 seconds
            if alert:
                try:
                    alert.dismiss()
                except:
                    try:  # 🚩 accept 시도 추가
                        alert.accept()
                    except NoAlertPresentException:
                        pass
                    except Exception: # accept 실패 시 강제 종료 시도
                        try:
                            driver.switch_to.alert.dismiss() # 🚩 강제 종료 시도
                        except NoAlertPresentException: # 알림창이 이미 없어진 경우
                            pass
                time.sleep(1)
        except TimeoutException: # 🚩 TimeoutException 처리 (알림창이 10초 안에 안 나타난 경우)
            pass
        except NoAlertPresentException: # 🚩 NoAlertPresentException 처리 (알림창이 없는 경우)
            pass


        
        # 로그아웃 시도 (로그아웃 버튼 존재 여부 확인)
        try:
            logout_button = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#top.header > div.navi > div > div > ul:nth-child(3) > li:nth-child(1) > a"))
            )
            if "로그아웃" in logout_button.text:  # 🚩 로그아웃 버튼 텍스트 확인
                logout_button.click()
                time.sleep(2)  # 로그아웃 후 대기
        except:
            pass  # 로그아웃 버튼을 찾을 수 없으면 아무것도 하지 않음.

        

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

        print(f"✅ [{profile_name}] 도매직방 로그인 성공!")
        return True

    except Exception as e:
        print(f"❌ [{profile_name}] 도매직방 로그인 중 오류 발생: {e}")
        return False






def navigate_to_order_details(driver, site_info, profile_name, collected_data):
    """도매직방 주문배송조회 페이지 이동 → 주문번호 목록에서 정보 수집 (상세 페이지 X) (프로필 이름 추가)"""
    try:
        print(f"\n[{profile_name}] 도매직방 주문배송조회 페이지 이동...")
        driver.get("https://www.dzb.co.kr/mypage/order_list.php")  # ✅ 수정된 주문배송조회 페이지 URL
        time.sleep(3)  # 페이지 로딩 대기

        print(f"✅ [{profile_name}] 도매직방 주문배송조회 페이지 이동 완료!")

        # 주문 목록 테이블의 각 행(주문) 가져오기
        order_rows = driver.find_elements(By.CSS_SELECTOR,
            "#content > div > div.contents-inner.mypage > div.section-body > div.mypage_table_type > table > tbody > tr") # ⚠️ 주문 목록 테이블 행 CSS selector (수정 필요할 수 있음)

        if not order_rows:
            print(f"[{profile_name}] ⚠️ 도매직방 주문 목록을 찾을 수 없음!")
            return False

        print(f"\n✅ [{profile_name}] 도매직방 주문 목록에서 정보 수집 시작:")

        # 오늘 날짜와 2일 전 날짜 계산 (최근 2일 주문 필터링 로직) ⚠️ 2일 전으로 수정
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        today_str = today.strftime("%y%m%d")
        yesterday_str = yesterday.strftime("%y%m%d")

        recent_days = [today_str, yesterday_str]
        print(f"\n🔎 [{profile_name}] 도매직방 최근 2일({recent_days}) 주문번호만 수집합니다.")

        # 주문 목록 순회하며 정보 추출
        for row in order_rows:
            try:
                order_number_element = row.find_element(By.CSS_SELECTOR, "td.order_day_num > a > span")
                order_number_text = order_number_element.text
                order_date_prefix = order_number_text[:6]  # 주문번호 앞 6자리가 날짜 (YYMMDD)

                if order_date_prefix in recent_days:  # 최근 2일 주문 필터링
                    print(f"\n📦 [{profile_name}] 주문번호: {order_number_text} 정보 수집...")

                    # 각 컬럼별 데이터 추출 (CSS selector 수정 필요)
                    delivery_info_element = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)")  # 배송정보
                    delivery_info_combined = delivery_info_element.text.strip()

                    recipient_name_element = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)")  # 받는 사람
                    recipient_name = recipient_name_element.text.strip()

                    delivery_company = "CJ택배"  # 배송사 CJ택배로 고정
                    delivery_number = "정보 없음"  # 기본값

                    # 배송정보에서 송장번호 추출 (10자리 이상 숫자)
                    #match = re.search(r'\d{10,}', delivery_info_combined)
                    #if match:
                     #   delivery_number = match.group(0)
                      #  print(f"✅ [{profile_name}] 송장번호 추출 성공: {delivery_number}")
                    #else:
                     #   print(f"⚠️ [{profile_name}] 송장번호 추출 실패: {delivery_info_combined}")



                    # 숫자와 문자를 분리하는 정규식 적용
                    match = re.search(r'(\D+)(\d+)', delivery_info_combined)  # 문자+숫자 그룹 찾기
                    if match:
                        recipient_name = match.group(1).strip()  # 문자(이름) 부분만 추출
                        delivery_number = match.group(2).strip()  # 숫자(송장번호) 부분만 추출
                    else:
                        recipient_name = delivery_info_combined  # 이름만 있을 경우
                        delivery_number = "정보 없음"

                    


                    # 수집된 정보 딕셔너리에 저장
                    order_detail = {
                        "site_name": site_info["site_name"],  # 🚩 공급사 이름 추가
                        "아이디": site_info["id"],
                        #"주문번호": order_number_text,
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
        print(f"❌ [{profile_name}] 도매직방 주문 배송 조회 페이지 작업 중 오류 발생: {e}")
        return False

def logout(driver, site_info, profile_name):
    """도매직방 로그아웃 수행 (프로필 이름 추가)"""
    try:
        print(f"\n[{profile_name}] 🚪 도매직방 로그아웃 시도...")
        # 로그아웃 버튼 클릭
        logout_button = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#top.header > div.navi > div > div > ul:nth-child(3) > li:nth-child(1) > a"))
            )
        if "로그아웃" in logout_button.text:  # 🚩 로그아웃 버튼 텍스트 확인
                logout_button.click()
                time.sleep(2)  # 로그아웃 후 대기
        
        
        print(f"✅ [{profile_name}] 도매직방 로그아웃 성공!")
        return True
    except Exception as e:
        print(f"❌ [{profile_name}] 도매직방 로그아웃 중 오류 발생: {e}")
        return False





def set_headless_option(options):
    """ChromeOptions에 헤드리스 모드 설정 추가"""
    options.add_argument("--headless")  # 헤드리스 모드 활성화
    options.add_argument("--disable-gpu")  # GPU 가속 비활성화 (일부 환경에서 필요)
    return options