import requests
import re
import io
import os
import traceback
from bs4 import BeautifulSoup
from PIL import Image

BASE_URL = "https://cs.sjtu.edu.cn"
IMG_STORE_DIR = "img"

def update_data():
  url = f"{BASE_URL}/NewNotice.aspx"
  # 使用Requests获取网页内容
  response = requests.get(url)
  html_content = response.text

  # 使用BeautifulSoup解析HTML
  soup = BeautifulSoup(html_content, "html.parser")

  # 提取包含“讲座”文本的链接
  lectures = []
  for a in soup.find_all('a', href=True):
    if a.text and re.search(r'讲座', a.text):
      lectures.append((a.text.strip(), f"{BASE_URL}/{a['href']}"))

  # 打印结果
  for title, link in lectures:
    print(f"{remove_date_prefix(title)}\n{link}")

  for title, link in lectures:
    download_img(title, link)
    pass

  return [title for title, link in lectures]

def download_img(name, link):
  os.makedirs(IMG_STORE_DIR, exist_ok=True)

  response = requests.get(link)
  soup = BeautifulSoup(response.content, "html.parser")
  images = soup.find_all("img")
  img_data = []
  for img in images:
    height = img.get("height")
    src = img.get("src")
    if height and src:
      try:
        height = int(height)
        img_data.append({"height": height, "src": src})
      except ValueError:
        traceback.print_exc()

  if len(img_data) == 0:
    print(f"no image at {link} (due to height check)")
    for img in images:
      src = img.get("src")
      if src and src.startswith("/Management/Common/KindEditor/attached/image"):
        img_data.append({"src": src})

  if len(img_data) == 0:
    print(f"no image at {link} (no fallback either)")
  
  if "height" in img_data[0]:
    target_img = max(img_data, key=lambda x: x["height"])
  else:
    target_img = img_data[0]

  img_src = f"{BASE_URL}{target_img['src']}"
  response = requests.get(img_src)
  img = Image.open(io.BytesIO(response.content))
  img.save(f"{IMG_STORE_DIR}/{name}.jpg")
  img.close()

def remove_date_prefix(title):
  # 正则表达式匹配形如 YYYY-MM-DD 的日期，并考虑其后可能存在的空白字符
  pattern = r'\d{4}-\d{2}-\d{2}\s*'
  # 使用正则表达式替换功能，将匹配到的日期替换为空字符串
  cleaned_title = re.sub(pattern, '', title)
  return cleaned_title.strip()
