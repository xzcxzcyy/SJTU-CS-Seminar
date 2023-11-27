from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
import io
from PIL import Image
import os
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import re

def get_driver():
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  driver = webdriver.Remote("http://chrome-standalone:4444/wd/hub", DesiredCapabilities.CHROME, options=chrome_options)
  return driver

CS_BASE_URL = "https://cs.sjtu.edu.cn/NewNotice.aspx"
IMG_STORE_DIR = "img"

def update_data(current: set):
  os.makedirs(IMG_STORE_DIR, exist_ok=True)
  addition = []

  driver = get_driver()
  # 进入指定网页
  driver.get(CS_BASE_URL) 

  # 找到包含"讲座"的所有链接
  links = driver.find_elements(By.PARTIAL_LINK_TEXT, "讲座")
  link_hrefs = [l.get_attribute("href") for l in links]
  link_names = [l.accessible_name for l in links]

  for link_href, link_name in zip(link_hrefs, link_names):
    if link_name in current:
      continue

    current.add(link_name)
    addition.append(link_name)

    filename = f"{IMG_STORE_DIR}/{link_name}.jpg"
    # 点击每个链接
    driver.get(link_href)

    # 等待页面加载完成 
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "html"))
    )

    images = driver.find_elements(By.TAG_NAME, "img")
    largest_img = max(images, key=lambda img: int(img.get_attribute("height")))

    # 从源代码中找到最大图片的src
    img_src = img_src = largest_img.get_attribute("src") 

    # 下载图片
    response = requests.get(img_src)
    img = Image.open(io.BytesIO(response.content))

    # 保存图片
    img.save(filename)
    img.close()
  driver.quit()
  return addition

def remove_date_prefix(title):
  # 正则表达式匹配形如 YYYY-MM-DD 的日期，并考虑其后可能存在的空白字符
  pattern = r'\d{4}-\d{2}-\d{2}\s*'
  # 使用正则表达式替换功能，将匹配到的日期替换为空字符串
  cleaned_title = re.sub(pattern, '', title)
  return cleaned_title.strip()
