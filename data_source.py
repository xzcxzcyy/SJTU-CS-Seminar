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

driver = None

def init_driver_if_need():
  global driver
  if driver is not None:
     return
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  driver = webdriver.Remote("http://chrome-standalone:4444/wd/hub", DesiredCapabilities.CHROME, options=chrome_options)

CS_BASE_URL = "https://cs.sjtu.edu.cn/NewNotice.aspx"
IMG_STORE_DIR = "img"

def update_data(current: set):
  init_driver_if_need()
  os.makedirs(IMG_STORE_DIR, exist_ok=True)
  addition = []

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
  return addition

def remove_date_prefix(input_string):
    # 使用split函数将字符串分割成日期和标题两部分，然后取第二部分作为结果
    parts = input_string.split(' ', 1)
    if len(parts) > 1:
        return parts[1]
    else:
        return input_string  # 如果没有空格分隔符，返回原始字符串
