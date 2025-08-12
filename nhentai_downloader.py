# -*- coding: utf-8 -*-
"""
Created on Fri Jun  6 19:51:27 2025

@author: user
"""

# N網抓圖小工具

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO

code = input("請輸入N網的號碼 : ")
base_url = 'https://nhentai.net/g/'+code+'/'

#連線至目標網頁
try:
    print("連線至網頁...")    
    html_response = requests.get(base_url)
    html_response.raise_for_status()
    print("網頁連線成功")
except requests.RequestException as e:
    print("網頁連線失敗：", e)
    exit()


#建立存放圖檔的資料夾Download_image
destDir = f'Download_{code}'

if os.path.exists(destDir) == False:
    os.mkdir(destDir)
 
   
# 解析作品頁面,取得所有頁數及分頁連結
html_soup = BeautifulSoup(html_response.text, 'lxml')
thumb_links = html_soup.select('.thumb-container > a')
print("頁數:", len(thumb_links))

for tag in thumb_links:
    #取得完整分頁的網址
    page_url = urljoin(base_url, tag.get('href'))
        
    try:
        print(f"{page_url} 連線至分頁中 ..." )
        page_response = requests.get(page_url)
        page_response.raise_for_status()
        print("分頁連線成功")
    except requests.RequestException as e:
        print("分頁連線失敗：", e)
        continue
    
    # 解析分頁取得圖片的url
    
# =============================================================================
#     #原本寫法
#     page_soup = BeautifulSoup(page_response.text, 'lxml')
#     img_tag = page_soup.select('img')
#     
#     # 第二個src才是圖片的url
#     img_url = img_tag[1].get('src')
# =============================================================================

    # Chatgpt的建議寫法
    page_soup = BeautifulSoup(page_response.text, 'lxml')
    img_tag = page_soup.select_one('#image-container img')    
       
    if not img_tag:
        print(f"未找到圖片：{page_url}")
        continue

    img_url = img_tag.get('src')
    
    if img_url.startswith('//'):
        img_url = 'https:' + img_url
    
    # 下載圖片
    try:
        print(f"{img_url} 圖片下載中 ..." )
        img_data = requests.get(img_url)
        img_data.raise_for_status() 
    except requests.RequestException as e:
        print("圖片下載失敗：", e)
        continue
        
# =============================================================================
#     # 原本寫法
#     # 取得圖片檔名
#     file_name = os.path.basename(img_url.split("?")[0])    
#     file_path = os.path.join(destDir, file_name)   
#       
#     # 儲存圖片    
#     with open(file_path, 'wb') as f:
#         for chunk in img_data.iter_content(10240):
#             f.write(chunk)
# =============================================================================
            
    # 開啟圖片並轉為 RGB（.webp 可能是透明背景
    image = Image.open(BytesIO(img_data.content)).convert("RGB")        
            
    # file_name = os.path.basename(img_url.split("?")[0])
    file_name = os.path.splitext(os.path.basename(img_url.split("?")[0]))[0] + ".jpg"
    file_path = os.path.join(destDir, file_name)          
    
    # Chatgpt, 儲存為 jpg
    image.save(file_path, format="JPEG", quality=95)
    print(f"{img_url} 圖片下載成功")

print("下載完成")
input("請按 Enter 結束...")
