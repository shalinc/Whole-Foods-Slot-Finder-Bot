from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from twilio.rest import Client
import time

# Define all the constants
HEADLESS_CHROME = 'headless'
CHROME_DRIVER_PATH = '../Downloads/chromedriver' # add path to your driver
AMAZON_SIGN_IN_URL = 'https://www.amazon.com/sign-in'
WHOLE_FOODS_CART_URL = 'https://www.amazon.com/cart/localmarket'
EMAIL_TEXT_ID = 'ap_email'
CONTINUE_BTN_ID = 'continue'
PASSWORD_BTN_ID = 'ap_password'
SIGN_IN_BTN_ID = 'signInSubmit'
CHECKOUT_BTN_ID = 'a-button-input'
CONTINUE_LINK_ID = 'Continue'
SCHEDULE_PAGE_TITLE_ID = 'ufss-widget-title'
SCHEDULE_YOUR_ORDER = 'Schedule your order'
SCHEDULE_SLOTS_ID = 'ufss-date-select-toggle-text-container'
NOT_AVAILABLE = "Not available"
REGISTERED_NUMBERS = #[ADD MOBILE NUMBERS HERE]
RETRY_TIME_SECONDS = 300.0

# set chrome options and create a webdriver
def init_chrome_webdriver():
    options = Options()
    options.add_argument(HEADLESS_CHROME);
    chrome_driver_path = CHROME_DRIVER_PATH
    driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
    return driver

# get user credentials for amazon sign in
def get_account_login_details():
    EMAIL_ADDRESS = input("Enter your Amazon email or phone number")
    AP_PWD = input("Enter your Amazon Account Password")
    return EMAIL_ADDRESS, AP_PWD

# sign in to amazon
def sign_in_amazon(EMAIL_ADDRESS, AP_PWD, driver):
    # goto amazon and sign in
    driver.get(AMAZON_SIGN_IN_URL)
    username_text_area_ele = driver.find_element_by_id(EMAIL_TEXT_ID)
    username_text_area_ele.send_keys(EMAIL_ADDRESS)
    continue_for_pwd_ele = driver.find_element_by_id(CONTINUE_BTN_ID)
    continue_for_pwd_ele.click()

    # wait for 5 secs
    driver.implicitly_wait(5)

    # enter password
    pwd_text_area_ele = driver.find_element_by_id(PASSWORD_BTN_ID)
    pwd_text_area_ele.send_keys(AP_PWD)
    sign_in_ele = driver.find_element_by_id(SIGN_IN_BTN_ID)
    sign_in_ele.click()

    driver.implicitly_wait(10)

# navigate to whole foods cart
def goto_whole_foods_checkout(driver):
    # goto whole foods page
    driver.get(WHOLE_FOODS_CART_URL)
    checkout_whole_foods_btn = driver.find_element_by_class_name(CHECKOUT_BTN_ID)
    checkout_whole_foods_btn.click()

    # before you checkout
    continue_btn_before_checkout = driver.find_element_by_link_text(CONTINUE_LINK_ID)
    continue_btn_before_checkout.click()

    # checkout on out of stock page, ignore substitutions
    continue_btn_substitutions = driver.find_element_by_class_name(CHECKOUT_BTN_ID)
    continue_btn_substitutions.click()

# send message to user if slot found
def send_message(to_number):
    account_sid = # account_sid
    auth_token = # account_auth_token
    # send a text message
    client = Client(account_sid, auth_token)
    message = client.messages \
                .create(
                     body="Hey, hurry up your delivery window slot is found. Check your amazon accout now. DO NOT REPLY.",
                     from_=# your twilio registered number,
                     to=to_number
                 )

    print(message.sid)

# check for schedule page and find slot, if found text the user
def check_for_slot_and_text(driver):
    # check if on delivery window page
    slot_found = False
    header_text_schedule_order = driver.find_element_by_class_name(SCHEDULE_PAGE_TITLE_ID)
    if header_text_schedule_order.text == SCHEDULE_YOUR_ORDER:
        # check if container select a day has unavailable option
        check_slot_options_eles = driver.find_elements_by_class_name(SCHEDULE_SLOTS_ID)
        print("checking for: ", len(check_slot_option_ele), "days")
        for slot_option in check_slot_options_eles:
            if NOT_AVAILABLE not in slot_option.text:
                print("Slot Found. Alerting user ...", slot_option.text)
                for to_number in REGISTERED_NUMBERS:
                    print('Sending Message')
                    send_message(to_number)
                slot_found = True
            else:
                print('Did not find slot for:', slot_option.text)
    return slot_found

# the whole foods slot finder flow
def main():
    EMAIL_ADDRESS, AP_PWD = get_account_login_details()
    driver = init_chrome_webdriver()
    sign_in_amazon(EMAIL_ADDRESS, AP_PWD, driver)
    goto_whole_foods_checkout(driver)
    slot_found = False
    starttime = time.time()
    # repeat until no slot found
    while not slot_found:
        slot_found = check_for_slot_and_text(driver)
        if slot_found:
            print('Notified User. Exiting App for the day')
            driver.close()
            break
        else: 
            print('Waiting for',(RETRY_TIME_SECONDS-((time.time() - starttime) % RETRY_TIME_SECONDS)), 'secs before checking again ...')
            time.sleep(RETRY_TIME_SECONDS - ((time.time() - starttime) % RETRY_TIME_SECONDS))
            driver.get(driver.current_url)

if __name__ == '__main__':
    main()