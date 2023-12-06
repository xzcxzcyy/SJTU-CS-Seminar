import base64
import requests
from PIL import Image
import io
import time
import json

MAX_TRY = 10
CLIENT_ID = "49694ef2-8751-4ac9-8431-8817c27350b4"
LIST_NAME = "SJTU Seminars"

def get_access_token(client_id, refresh_token):
  token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
  data = {
    "grant_type": "refresh_token",
    "client_id": client_id,
    "refresh_token": refresh_token,
    "scope": "Tasks.ReadWrite User.Read offline_access"
  }
  response = requests.post(token_url, data=data)
  if response.status_code == 200:
    token = response.json()
    return token["access_token"], token["refresh_token"]
  else:
    print(f"获取访问令牌时出错：{response.text}")
    return None

def create_todo_list(access_token, list_name):
  headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
  }
  
  # 创建待办列表
  create_list_url = "https://graph.microsoft.com/v1.0/me/todo/lists"
  data = {
    "displayName": list_name
  }
  response = requests.post(create_list_url, headers=headers, json=data)
  if response.status_code == 201:
    print(f"已创建待办列表 '{list_name}'")
  elif response.status_code == 409:
    print(f"待办列表 '{list_name}' 已经存在")
  else:
    print(f"创建待办列表时出错：{response.text}")

def check_or_create_todo_item(access_token, list_name, todo_title, image_path):
  headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
  }
  
  # 获取待办列表的ID
  def get_lists():
    list_id_url = f"https://graph.microsoft.com/v1.0/me/todo/lists?$filter=displayName eq '{list_name}'"
    response = requests.get(list_id_url, headers=headers)
    lists = response.json()["value"]
    return lists
  
  def list_exist():
    lists = get_lists()
    if lists:
      return True
    return False
  
  if not list_exist():
    print("no list. creating one")
    create_todo_list(access_token, list_name)

  i = 0
  while not list_exist():
    i += 1
    if i >= MAX_TRY:
      print(f"creating list error. {list_name} does not show up.")
      return
    time.sleep(1.0)
  
  list_id = get_lists()[0]["id"]
  
  # 检查待办项是否存在
  check_item_url = f"https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks?$filter=title eq '{todo_title}'"
  response = requests.get(check_item_url, headers=headers)
  tasks = response.json().get("value")
  if tasks:
    print(f"待办项 '{todo_title}' 已经存在")
    return
  
  create_item_url = f"https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks"
  data = {
    "title": todo_title
  }
  response = requests.post(create_item_url, headers=headers, json=data)
  if response.status_code == 201:
    print(f"已创建待办项 '{todo_title}'")
    item_id = response.json()["id"]
    upload_image_url = f"https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks/{item_id}/attachments"
    upload_image(image_path, access_token, upload_image_url)
  else:
    print(f"创建待办项时出错：{response.text}")

def upload_image(image_path, access_token, upload_image_url):
  headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
  }

  # 使用Pillow库打开并读取图片
  with open(image_path, "rb") as image_file:
    image_data = image_file.read()
  
  # 检测图片格式并设置相应的Content-Type
  image_format = Image.open(io.BytesIO(image_data)).format
  if image_format == "JPEG":
    content_type = "image/jpeg"
  elif image_format == "PNG":
    content_type = "image/png"
  elif image_format == "GIF":
    content_type = "image/gif"
  else:
    content_type = "application/octet-stream"
  upload_body = {
    "@odata.type": "#microsoft.graph.taskFileAttachment",
    "name": f"详细信息.{image_format.lower()}",
    "contentBytes": base64.b64encode(image_data).decode("utf-8"),
    "contentType": content_type,
    "size": len(image_data)
  }

  response = requests.post(upload_image_url, headers=headers, json=upload_body)
  if response.status_code == 201:
    print("已上传图片")
  else:
    print(f"上传图片时出错：{response.text}")
