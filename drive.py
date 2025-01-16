from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
import re
import multiprocessing


def parse_time_ago(time_str):
    match = re.match(r"(\d+)\s+(лет|год|года|месяц|месяца|месяцев|недель|неделя|недели|день|дня|дней|час|часа|часов"
                     r"|минут|минуту|минуты|секунда|секунды|секунд)", time_str)

    amount, unit = match.groups()
    amount = int(amount)
    exact_date = datetime.now()
    if unit.startswith('год') or unit.startswith('лет'):
        exact_date = datetime.now() - relativedelta(years=amount)
    elif unit.startswith('месяц'):
        exact_date = datetime.now() - relativedelta(months=amount)
    elif unit.startswith('недел'):
        exact_date = datetime.now() - relativedelta(weeks=amount)
    elif unit.startswith('день') or unit.startswith('дн'):
        exact_date = datetime.now() - relativedelta(days=amount)
    elif unit.startswith('час'):
        exact_date = datetime.now() - relativedelta(hours=amount)
    elif unit.startswith('минут'):
        exact_date = datetime.now() - relativedelta(minutes=amount)
    elif unit.startswith('секунд'):
        exact_date = datetime.now() - relativedelta(seconds=amount)
    return exact_date.strftime('%Y-%m-%d')


def parse_one_marque(model_name):
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    data = []
    try:
        driver.get('https://www.drive2.ru/')
        # driver.maximize_window()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        h = driver.execute_script("return document.documentElement.scrollHeight")
        time.sleep(1)
        link_all = driver.find_element("xpath", '/html/body/main/div[2]/button')  # кнопка "все марки машин"
        link_all.click()
        time.sleep(1)
        element = driver.find_element(By.LINK_TEXT, model_name)
        for i in range(h, 0, -100):
            driver.execute_script(f"window.scrollTo(0, {i})")
            time.sleep(1)
            element = driver.find_element(By.LINK_TEXT, model_name)
            try:
                element.click()
                break
            except:
                continue
        time.sleep(1)
        driver.set_page_load_timeout(5)
        posts_preview = driver.find_elements(By.CLASS_NAME, 'c-post-preview__lead')
        car_title = driver.find_elements(By.CLASS_NAME, 'c-car-card__caption')
        date = driver.find_elements(By.CLASS_NAME, 'c-author__date')
        pic = driver.find_elements(By.CLASS_NAME, 'c-preview-pic')
        title = driver.find_elements(By.CLASS_NAME, 'c-post-preview__title')
        current = None
        for i in range(len(posts_preview)):
            try:
                data.append(dict())
                # print(car_title[i].text)
                data[-1]["Модель автомобиля"] = car_title[i].text
                # print(parse_time_ago(date[i].text))
                data[-1]["Время публикации"] = parse_time_ago(date[i].text)
                # print(posts_preview[i].text)
                post_url = title[i].find_element(By.TAG_NAME, 'a').get_attribute('href')
                driver.execute_script(f"window.open('{post_url}', '_blank');")
                WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
                driver.switch_to.window(driver.window_handles[1])
                paragraph = driver.find_elements(By.CLASS_NAME, "c-link-decorated")
                desc = ""
                for elem in paragraph:
                    if "Войдите или зарегистрируйтесь" in elem.text:
                        break
                    else:
                        # print(elem.text)
                        desc += elem.text
                data[-1]["Описание"] = desc
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
        time.sleep(3)
        h = driver.execute_script("return document.documentElement.scrollHeight")
        driver.execute_script(f"window.scrollTo(0, {h - 1100})")
        time.sleep(1)
        element2 = driver.find_element(By.LINK_TEXT, 'Следующие')
        element2.click()
        time.sleep(3)
        while True:
            driver.set_page_load_timeout(5)
            posts_preview = driver.find_elements(By.CLASS_NAME, 'c-post-preview__lead')
            car_title = driver.find_elements(By.CLASS_NAME, 'c-car-card__caption')
            date = driver.find_elements(By.CLASS_NAME, 'c-author__date')
            pic = driver.find_elements(By.CLASS_NAME, 'c-preview-pic')
            title = driver.find_elements(By.CLASS_NAME, 'c-post-preview__title')
            current = None
            for i in range(len(posts_preview)):
                try:
                    data.append(dict())
                    # print(car_title[i].text)
                    data[-1]["Модель автомобиля"] = car_title[i].text
                    # print(parse_time_ago(date[i].text))
                    data[-1]["Время публикации"] = parse_time_ago(date[i].text)
                    # print(posts_preview[i].text)
                    post_url = title[i].find_element(By.TAG_NAME, 'a').get_attribute('href')
                    driver.execute_script(f"window.open('{post_url}', '_blank');")
                    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
                    driver.switch_to.window(driver.window_handles[1])
                    paragraph = driver.find_elements(By.CLASS_NAME, "c-link-decorated")
                    desc = ""
                    for elem in paragraph:
                        if "Войдите или зарегистрируйтесь" in elem.text:
                            break
                        else:
                            # print(elem.text)
                            desc += elem.text
                    data[-1]["Описание"] = desc
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue
            h = driver.execute_script("return document.documentElement.scrollHeight")
            driver.execute_script(f"window.scrollTo(0, {h - 1000})")
            time.sleep(5)
            try:
                element2 = driver.find_elements(By.LINK_TEXT, 'Следующие')[-1]
                element2.click()
                time.sleep(3)
            except:
                break
        back = driver.find_element("xpath", "/html/body/header/div/div/a")  # возвращение на главную страницу
        back.click()
    finally:
        driver.quit()
        df = pd.DataFrame(data)
        df.to_csv('drive2_' + model_name + '.csv', index=False, encoding='utf-8-sig', sep=';')


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    data = []
    try:
        driver.get('https://www.drive2.ru/')
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        height = driver.execute_script("return document.documentElement.scrollHeight")
        time.sleep(1)
        all_link = driver.find_element("xpath", '/html/body/main/div[2]/button')  # кнопка "все марки машин"
        all_link.click()
        time.sleep(1)
        marques = driver.find_elements(By.XPATH, '/html/body/main/div[2]/div[3]')
        s = []
        for elem in marques:
            s.append(elem.text)
        all_marques = s[0].split('\n')[:-2]  # список всех марок
    finally:
        driver.quit()
    for i in range(95):
        start = 2 * i
        end = start + 2
        batch = all_marques[start:end]
        processes = []
        for model in batch:
            process = multiprocessing.Process(target=parse_one_marque, args=(model,))
            processes.append(process)
            process.start()
        for process in processes:
            process.join()

