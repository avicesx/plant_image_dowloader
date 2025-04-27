import os
import json
import time
import random
import pandas as pd
import aiohttp
import asyncio
from PIL import Image
from io import BytesIO
from selenium import webdriver
from urllib.parse import parse_qs, urlparse, unquote
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def urls_scraper(plant_name):

    def scroll_to_bottom(driver, button: str=None, delay=5, max_scrolls=20):
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(max_scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(delay)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                try:
                    button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, button)))
                    if button:
                        button.click()
                        time.sleep(4)
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                except:
                    break
            last_height = new_height


    def from_bing():
        searcher_site = "https://www.bing.com/images"
        driver.get(searcher_site)
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
        search_box.clear()
        search_box.send_keys(plant_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(4)
        scroll_to_bottom(driver, "a.btn_seemore")
        thumbs = driver.find_elements(By.CSS_SELECTOR, "a.iusc")
        print(f"В bing найдено миниатюр: {len(thumbs)}")
        pic_urls = []
        for i, thumb in enumerate(thumbs):
            try:
                metadata = thumb.get_attribute("m")
            except Exception as e:
                print(f"[{i + 1}] Ошибка при парсинге JSON: {e}")
                continue
            data = json.loads(metadata)
            url = data.get("murl")  # оригинальный URL картинки
            if url and url.startswith("http"):
                pic_urls.append(url)
        print(f"Парсинг bing позволил получить url картинок в количестве: {len(pic_urls)}")

        return pic_urls


    def from_yahoo():
        searcher_site = "https://images.search.yahoo.com/"
        driver.get(searcher_site)
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "p")))
        search_box.clear()
        search_box.send_keys(plant_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(4)
        scroll_to_bottom(driver, "button.more-res")
        thumbs = driver.find_elements(By.CSS_SELECTOR, "li.ld")
        print(f"В yahoo найдено миниатюр: {len(thumbs)}")
        pic_urls = []
        for i, thumb in enumerate(thumbs):
            try:
                a_tag = thumb.find_element(By.TAG_NAME, "a")
                metadata = a_tag.get_attribute("href")
                if not metadata:
                    continue
                parsed = urlparse(metadata)
                params = parse_qs(parsed.query)
                url = params.get("imgurl", [None])[0]
                scheme = urlparse(params.get("rurl", [None])[0]).scheme
                if url:
                    pic_urls.append(unquote(f"{scheme}://{url}"))

            except Exception as e:
                print(f"[{i + 1}] Ошибка при парсинге JSON: {e}")
                continue
        print(f"Парсинг yahoo позволил получить url картинок в количестве: {len(pic_urls)}")

        return pic_urls


    def from_yandex():
        searcher_site = "https://ya.ru/images"
        driver.get(searcher_site)
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "text")))
        search_box.clear()
        search_box.send_keys(plant_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(4)
        scroll_to_bottom(driver, "button.FetchListButton-Button")
        thumbs = driver.find_elements(By.CSS_SELECTOR, "a.ImagesContentImage-Cover")
        print(f"В yandex найдено миниатюр: {len(thumbs)}")
        pic_urls = []
        for i, thumb in enumerate(thumbs):
            try:
                metadata = thumb.get_attribute("href")
                if not metadata:
                    continue
                parsed = urlparse(metadata)
                params = parse_qs(parsed.query)
                url = params.get("img_url", [None])[0]
                if url:
                    pic_urls.append(unquote(url))

            except Exception as e:
                print(f"[{i + 1}] Ошибка при парсинге JSON: {e}")
                continue
        print(f"Парсинг yandex позволил получить url картинок в количестве: {len(pic_urls)}")

        return pic_urls

    def from_google():
        searcher_site = "https://www.google.com/imghp"
        driver.get(searcher_site)
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
        search_box.clear()
        search_box.send_keys(plant_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(4)
        scroll_to_bottom(driver)
        thumbs = driver.find_elements(By.CSS_SELECTOR, "h3.ob5Hkd")
        print(f"В google найдено миниатюр: {len(thumbs)}")
        pic_urls = []
        action = ActionChains(driver)
        for i, thumb in enumerate(thumbs):
            try:
                action.move_to_element(thumb).perform()
                # time.sleep(0.1)
                a_tag = thumb.find_element(By.TAG_NAME, "a")
                metadata = a_tag.get_attribute("href")
                if not metadata:
                    continue
                parsed = urlparse(metadata)
                params = parse_qs(parsed.query)
                url = params.get("imgurl", [None])[0]
                if url:
                    pic_urls.append(unquote(url))

            except Exception as e:
                print(f"[{i + 1}] Ошибка при парсинге JSON: {e}")
                continue
        print(f"Парсинг google позволил получить url картинок в количестве: {len(pic_urls)}")

        return pic_urls


    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=2560,1440")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    all_urls = from_bing() + from_yahoo() + from_yandex() + from_google()
    driver.quit()

    all_urls_set = set(all_urls)
    print(f"Из {len(all_urls)} осталось {len(all_urls_set)} оригинальных ссылок.\nНачинаю скачивание.")

    return all_urls_set


async def download_image(
    session: aiohttp.ClientSession,
    url: str,
    target_folder: str,
    headers: dict,
    ind_url: int,
    proxies_list: list,
    retries: int = 3,
    delay: int = 5
) -> None:
    """
    Загружает изображение по URL с несколькими попытками при ошибках.
    Использует заданный proxy и случайный User-Agent.
    """

    for attempt in range(retries):
        try:
            current_headers = {"User-Agent": random.choice(USER_AGENTS), **headers}
            proxy = None
            if proxies_list:
                proxy = random.choice(proxies_list)
            timeout = aiohttp.ClientTimeout(
                total=30,
                connect=20,
                sock_connect=20,
                sock_read=20
            )

            async with session.get(url, headers=current_headers, timeout=timeout, proxy=proxy) as response:
                if response.status == 200:

                    image_data = await response.read()

                    loop = asyncio.get_event_loop()
                    try:
                        img = await loop.run_in_executor(None, lambda: Image.open(BytesIO(image_data)))
                    except:
                        print(f"Похоже, там не картинка: {url}. Пробовал этот proxy: {proxy}. Пробовал этот user-agent: {current_headers["User-Agent"]}")
                        return

                    try:
                        await loop.run_in_executor(None, img.load)
                        if img.size[0] < min_width or img.size[1] < min_height:
                            print(f"Пропущено (маленькое): {url}")
                            return
                    except:
                        print(f"Что-то с ссылкой {url}")
                        return

                    parsed_url = urlparse(url)
                    ext = parsed_url.path.split('.')[-1].lower()
                    if ext not in ALLOWED_EXTENSIONS:
                        print(f"Неподходящее расширение: {ext} для {url}")
                        return

                    filename = os.path.join(target_folder, f"image_{ind_url}.{ext}")

                    try:
                        await loop.run_in_executor(None, lambda: img.save(filename))
                        print(f"Скачано с попытки {attempt+1}: {url}. Удачное proxy: {proxy}. Удачный user-agent: {current_headers["User-Agent"]}")
                    except:
                        print(
                            f"Не шмог сохранить: {url}. Удачное proxy: {proxy}. Удачный user-agent: {current_headers["User-Agent"]}")
                    return

                print(f"Попытка {attempt + 1}: Ошибка HTTP {response.status} для {url}. Пробовал этот proxy: {proxy}. Пробовал этот user-agent: {current_headers["User-Agent"]}")
                await asyncio.sleep(delay)

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            # Обработка сетевых ошибок и таймаутов
            print(f"Попытка {attempt + 1} не удалась для {url}: {e}")
            if attempt < retries - 1:
                print(f"Повтор через {delay} сек...")
                await asyncio.sleep(delay)

    print(f"Не удалось скачать: {url} (все {retries} попытки исчерпаны)")


async def download_all(
    urls: set[str],
    target_folder: str,
    headers: dict = None,
    max_parallel: int = 5,
    proxies: list = None
) -> None:
    """
    Асинхронно скачивает все изображения из списка URL.
    Ограничивает число одновременных загрузок с помощью семафора.
    """

    base_headers = headers or {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    semaphore = asyncio.Semaphore(max_parallel)

    async with aiohttp.ClientSession() as session:
        async def wrapped_download(idx: int, url: str):
            async with semaphore:
                print(f"[{idx + 1}/{len(urls)}] Загрузка: {url}")
                await download_image(
                    session=session,
                    url=url,
                    target_folder=target_folder,
                    headers=base_headers,
                    ind_url=idx,
                    proxies_list=proxies,
                    retries=3,
                    delay=5
                )

        tasks = [
            asyncio.create_task(wrapped_download(idx, url))
            for idx, url in enumerate(urls)
        ]
        await asyncio.gather(*tasks)


async def check_proxy(
        session: aiohttp.ClientSession,
        proxy_url: str,
        test_url: str,
) -> bool:
    """
    Проверяет прокси используя существующую сессию
    """
    current_headers = {"User-Agent": USER_AGENTS[0]}
    timeout = aiohttp.ClientTimeout(total=15)
    try:
        async with session.get(test_url, headers=current_headers, timeout=timeout, proxy=proxy_url) as response:
            return response.status == 200
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return False


async def mass_check_proxy(proxies: list, test_url: str) -> list:
    """
    Массовая проверка прокси
    """
    working_proxies = []
    print("Начинаю проверку proxy...")
    async with aiohttp.ClientSession() as session:
        tasks = [check_proxy(session, proxy, test_url) for proxy in proxies]
        results = await asyncio.gather(*tasks)
        for proxy, status in zip(proxies, results):
            if status:
                working_proxies.append(proxy)
    print(f"Из {len(proxies)} прокси работающих {len(working_proxies)} штуки:\n{working_proxies}")
    return working_proxies


main_folder = r"PATH"
num_images = 200
min_width = 1000
min_height = 1000
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
]
custom_headers = \
          {"sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
           "sec-ch-ua-mobile": "?0",
           "sec-ch-ua-model": '""',
           "sec-ch-ua-platform-version": '"20.0.0"',
           "sec-ch-ua-platform": "Windows",
           "sec-ch-ua-arch": '"x86"',
           "sec-ch-ua-full-version-list": '"Google Chrome";v="135.0.7049.84", "Not-A.Brand";v="8.0.0.0", "Chromium";v="135.0.7049.84"',
           "sec-fetch-dest": "document",
           "sec-fetch-mode": "navigate",
           "sec-fetch-site": "none",
           "sec-fetch-user": "?1",
           "upgrade-insecure-requests": "1",
           "dnt": "1",
           "accept-language": "ru,ru-RU;q=0.9,en-US;q=0.8,en;q=0.7",
           "accept-encoding": "gzip, deflate, br, zstd",
           "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
           "cache-control": "max-age=0",
           "priority": "u=0, i"
           }
PROXIES = [
    "http://PROXY",
    "http://PROXY",
    None  # Прямое соединение
]

df = pd.read_csv("FILE.csv", sep=",")
for plant_name in df["COLUMN_NAME"]:
    print(plant_name)
    target_folder = os.path.join(main_folder, plant_name)
    os.mkdir(target_folder)
    print(f"Папка '{target_folder}' создана")

    finded_urls = urls_scraper(plant_name)
    working_proxies = asyncio.run(mass_check_proxy(PROXIES, "https://httpbin.org/ip"))

    with open(os.path.join(target_folder, "finded_urls.txt"), "w",  encoding="utf-8") as file:
        for line in finded_urls:
            file.write(f"{line}\n")

    asyncio.run(download_all(finded_urls, target_folder, custom_headers, max_parallel=10, proxies=working_proxies))

    print(f"\nКартинки {plant_name} скачаны в папку '{target_folder}'.")

print("Фух, закончили")