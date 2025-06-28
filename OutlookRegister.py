import time
import random
import string
import secrets
from faker import Faker
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor

def generate_strong_password(length=16):

    chars = string.ascii_letters + string.digits + "!@#$%^&*"

    while True:
        password = ''.join(secrets.choice(chars) for _ in range(length))

        if (any(c.islower() for c in password) 
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*" for c in password)):
            return password


def random_email(length):

    first_char = random.choice(string.ascii_lowercase)

    other_chars = []
    for _ in range(length - 1):  
        if random.random() < 0.07:  
            other_chars.append(random.choice(string.digits))
        else: 
            other_chars.append(random.choice(string.ascii_lowercase))

    return first_char + ''.join(other_chars)

def OpenBrowser():
    try:
        p = sync_playwright().start()
        browser = p.chromium.launch(
            executable_path=browser_path,
            headless=True,
            proxy={
                "server": proxy,
                "bypass": "localhost",
            },
        ) 
        return browser,p

    except Exception as e:
        print(e)

def Outlook_register(browser, email, password):

    page = browser.new_page()
    fake = Faker()

    lastname = fake.last_name()
    firstname = fake.first_name()
    year = str(random.randint(1960, 2005))
    month = str(random.randint(1, 12))
    day = str(random.randint(1, 28))

    try:

        page.goto("https://outlook.live.com/mail/0/?prompt=create_account", timeout=20000, wait_until="domcontentloaded")
        page.get_by_text('同意并继续').click(timeout=30000)

    except: 

        print("无法进入注册界面，建议更换IP！ ")
        return False
    
    try:

        page.locator('[aria-label="新建电子邮件"]').type(email,delay=50,timeout=10000)
        page.locator('[data-testid="primaryButton"]').click(timeout=5000)
        page.locator('[type="password"]').type(password,delay=50,timeout=10000)
        page.locator('[data-testid="primaryButton"]').click(timeout=5000)
        
        page.wait_for_timeout(500)
        page.locator('[name="BirthYear"]').type(year,delay=50,timeout=10000)

        try:

            page.locator('[name="BirthMonth"]').select_option(value=month,timeout=2000)
            page.locator('[name="BirthDay"]').select_option(value=day)
        
        except:

            page.locator('[name="BirthMonth"]').click()
            page.locator(f'[role="option"]:text-is("{month}月")').click()
            page.locator('[name="BirthDay"]').click()
            page.locator(f'[role="option"]:text-is("{day}日")').click()

        page.locator('[data-testid="primaryButton"]').click(timeout=5000)

        page.locator('#lastNameInput').type(lastname,delay=50,timeout=10000)
        page.locator('#firstNameInput').type(firstname,delay=48,timeout=10000)
        page.locator('[data-testid="primaryButton"]').click(timeout=5000)
        page.locator('span > [href="https://go.microsoft.com/fwlink/?LinkID=521839"]').wait_for(state='detached',timeout=10000)

        page.wait_for_timeout(700)

        if page.get_by_text('一些异常活动').count() > 0:
            print("IP不够纯净或者机器人检查未通过，请检查浏览器！！")
            return False

        if page.locator('iframe#enforcementFrame').count() > 0:
            print("这是FunCaptcha，并非px按压，对应内容请自行处理。")
            return False

        page.wait_for_event("request", lambda req: req.url.startswith("blob:https://iframe.hsprotect.net/"), timeout=20000)
        page.wait_for_timeout(1000)

        page.keyboard.press('Tab')
        page.keyboard.press('Tab')
        page.wait_for_timeout(100)

        page.keyboard.press('Enter')
        page.wait_for_timeout(11000)
        page.keyboard.press('Enter')
        
        page.locator('[data-testid="secondaryButton"]').click(timeout=25000) 
        button = page.locator('[data-testid="secondaryButton"]')
        button.wait_for(timeout=5000)
        
    except Exception as e:

        print(f"等待时间过长或按压未通过，请检查IP。")
        return False   

    try:

        page.wait_for_timeout(random.randint(1600,2400))
        button.click(timeout=6000)
        button = page.locator('[data-testid="secondaryButton"]')
        button.wait_for(timeout=5000)
        page.wait_for_timeout(random.randint(1600,2400))
        button.click(timeout=6000)
        button = page.locator('[data-testid="secondaryButton"]')
        button.wait_for(timeout=5000)
        page.wait_for_timeout(4000)
        button.click(timeout=6000)

    except:
        pass

    try:
        page.wait_for_timeout(3200)
        if page.get_by_text("保持登录状态?").count() > 0:
            page.get_by_text('否').click(timeout=12000)

    except Exception as e:
        print(f"错误：{e}")
        return False

    try:
        page.locator('.splitPrimaryButton[aria-label="新邮件"]').wait_for(timeout=24000)
        return True
    except:
        print(f'未进入邮箱界面，可能无法使用Token收件。')
        return False

def process_single_flow():

    try:
        browser = None
        browser, p = OpenBrowser()

        email =  random_email(random.randint(12, 14))
        password = generate_strong_password(random.randint(11, 15))
        result = Outlook_register(browser, email, password)
        if result:
            with open('result.txt', 'a', encoding='utf-8') as f:
                f.write(f"{email}@outlook.com: {password}\n")
            print(f'注册成功 - {email}@outlook.com: {password}')
            return True
    except:
        return False

    finally:
        browser.close()
        p.stop()

def main(concurrent_flows=10, max_tasks=1000):

    task_counter = 0  
    succeeded_tasks = 0 
    failed_tasks = 0 

    with ThreadPoolExecutor(max_workers=concurrent_flows) as executor:
        running_futures = set()

        while task_counter < max_tasks or len(running_futures) > 0:

            done_futures = {f for f in running_futures if f.done()}
            for future in done_futures:
                try:
                    result = future.result()
                    if result:
                        succeeded_tasks += 1
                    else:
                        failed_tasks += 1

                except Exception as e:
                    failed_tasks += 1
                    print(e)

                running_futures.remove(future)
            
            while len(running_futures) < concurrent_flows and task_counter < max_tasks:
                time.sleep(0.2)
                new_future = executor.submit(process_single_flow)
                running_futures.add(new_future)
                task_counter += 1

            time.sleep(0.5)

        print(f"所有任务已完成 - 共 {max_tasks} 个，成功 {succeeded_tasks}，失败 {failed_tasks}")

if __name__ == '__main__':


    target_url = 'https://outlook.live.com/mail/0/?prompt=create_account'
    # 使用本地代理, 可以自行调整为IP池
    proxy = 'http://127.0.0.1:7897'

    browser_path = r""

    main(concurrent_flows=2, max_tasks=10)