import datetime
from flask import Flask, request, jsonify
import json
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

import ms_todo
import data_source_bs
from data_source_bs import IMG_STORE_DIR

app = Flask(__name__)
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

CONFIG_FILE = "config.json"

# 读取配置项的值
def read_config(key):
  with open(CONFIG_FILE, "r") as file:
    config = json.load(file)
    return config.get(key)
  
# 读取所有配置项的值
def read_all_config():
  with open(CONFIG_FILE, "r") as file:
    config = json.load(file)
    return config

# 写入配置项的值
def write_config(key, value):
  with open(CONFIG_FILE, "r") as file:
    config = json.load(file)
  config[key] = value
  with open(CONFIG_FILE, "w") as file:
    json.dump(config, file, indent=2)

@app.route("/update_seminars", methods=["POST"])
def update_seminars():
  result = process_once()
  ret = {
    "message": "success",
    "result": result
  }
  return jsonify(ret)

@app.route("/get_config", methods=["GET"])
def get_config():
  all_config = read_all_config()
  return jsonify(all_config)

@app.route("/set_config", methods=["POST"])
def set_config():
  data = request.get_json()
  for key, value in data.items():
    write_config(key, value)
  return jsonify({"message": "success"})

@app.route("/start_timer", methods=["POST"])
def start_timer():
  update_period_min = read_config("update_period_min")
  if update_period_min is None:
    return jsonify({"message": "you should set update_period_min"})
  
  scheduler.remove_all_jobs()
  scheduler.add_job(process_once, "interval", minutes=update_period_min, next_run_time=datetime.datetime.now())

  return jsonify({"message": "success"})

@app.route("/stop_timer", methods=["POST"])
def stop_timer():
  scheduler.remove_all_jobs()
  return jsonify({"message": "success"})

def update_todo(todo_title, img_path):
  config = read_all_config()
  refresh_token = config["refresh_token"]
  client_id = config["client_id"]
  list_name = config["list_name"]
  access_token, new_refresh = ms_todo.get_access_token(client_id, refresh_token)
  write_config("refresh_token", new_refresh)
  ms_todo.check_or_create_todo_item(access_token, list_name, todo_title, img_path)

def process_once():
  """Get seminars and update ToDo List.
  return new found seminars
  """
  addition = data_source_bs.update_data()
  print(f"process_once get seminar list: {addition}")
  for full_title in addition:
    title = data_source_bs.remove_date_prefix(full_title)
    img_path = f"{IMG_STORE_DIR}/{full_title}.jpg"
    update_todo(title, img_path)
  return addition

if __name__ == "__main__":
  app.run(debug=False, port=5000, host="0.0.0.0")
