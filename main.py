# -*- coding: utf-8 -*-
"""
Python Script for Auto-download images under user-defined requirements

Created on Thu Oct 19 15:49:35 2023

@author: Kunru Song
"""
# -*- coding: utf-8 -*-
import os
import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import imagehash
import random
import time
import cv2
import numpy as np

PAGES_TO_SCRAP = 10  # 根据需要增加此值来获取更多的图片
MAX_ATTEMPTS = 100

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
    "Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36 Edge/13.10586",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
]


def get_random_user_agent():
    return random.choice(USER_AGENTS)


def fetch_image_links_from_bing(query, num_images, page=1):
    print("Fetching image links from Bing...")

    OFFSET = 0  # 每页的图片数量，可以根据Bing的实际情况进行调整

    urls = []

    while len(urls) < num_images:
        search_url = f'https://www.bing.com/images/search?q={query}&form=HDRSC2&first={page * OFFSET + 1}'
        headers = {
            "User-Agent": get_random_user_agent()
        }
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all("img", class_="mimg")

        new_urls = [img['src'] for img in img_tags if img.has_attr('src') and 'data:image' not in img['src']]
        if not new_urls:  # 如果没有新的图片链接，停止搜索
            break

        urls.extend(new_urls)
        page += 1  # 增加页面计数以获取下一页的图片

        time.sleep(random.uniform(2, 5))  # 在请求之间添加延迟

    print(f"Fetched {len(urls)} image links from Bing.")
    return urls[:num_images]


def download_images(query, resolution, num_images):
    print("Starting image download...")
    os.makedirs(query, exist_ok=True)

    # 获取图片链接
    img_urls = fetch_image_links_from_bing(query, num_images)

    downloaded_hashes = set()
    count = 0
    attempts = 0

    for image_url in img_urls:
        try:
            headers = {
                "User-Agent": get_random_user_agent()
            }
            response = requests.get(image_url, headers=headers)
            img = Image.open(BytesIO(response.content))

            # 检查响应状态
            if response.status_code != 200:
                print(f"Error! Received status code {response.status_code} from {image_url}.")
                continue

            # # 如果图片的原始分辨率小于所需分辨率，跳过这张图片
            # if img.width < resolution[0] or img.height < resolution[1]:
            #     print(f"Skipped! Raw resolution of source images is below than requirements")
            #     continue

            # 调整图片分辨率
            img = img.resize(resolution)

            # 使用感知哈希检测重复的图片
            img_hash = imagehash.average_hash(img)
            if img_hash not in downloaded_hashes:
                downloaded_hashes.add(img_hash)

                # 去除水印（示例代码，实际中可能需要更复杂的算法）
                img_array = np.array(img)
                gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
                img_array = cv2.inpaint(img_array, mask, 3, cv2.INPAINT_TELEA)
                img_without_watermark = Image.fromarray(img_array)

                # 保存图片
                img_without_watermark.save(os.path.join(query, f'{count + 1}.jpg'))
                print(f"Downloaded and saved image {count + 1} to folder '{query}'.")
                count += 1
            else:
                print(f"Skipped! Duplicated image was detected!")

            time.sleep(random.uniform(2, 5))

        except Exception as e:
            print(f"Error downloading image from {image_url}: {str(e)}")

        attempts += 1

        if count >= num_images or attempts >= MAX_ATTEMPTS:
            break

    print(f"Download complete! Images saved in folder: '{os.path.abspath(query)}'")


if __name__ == "__main__":
    resolution = tuple(map(int, input("请输入图片分辨率（例如800 600）：").split()))
    num_images = int(input("请输入要下载的图片数量："))

    while True:
        query = input("请输入搜索主题词（输入'exit'以结束）：").strip()  # 使用strip()移除字符串两侧的空白字符
        if not query:  # 如果输入为空
            print("输入不能为空，请重新输入。")
            continue  # 跳过本次循环，继续下一次输入
        if query.lower() == 'exit':
            break

        # 执行图片下载
        download_images(query, resolution, num_images)
