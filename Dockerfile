# 使用官方Python 3.11.5映像作为基础映像
FROM python:3.11.5-slim as base

FROM base as builder

COPY requirements.txt /requirements.txt
RUN pip install --upgrade --no-cache-dir -r /requirements.txt
RUN rm /requirements.txt

# 设置工作目录
WORKDIR /app

# 复制文件到工作目录
COPY *.py /app/
COPY config.json /app/

FROM builder

WORKDIR /app
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# 暴露Flask应用程序运行的端口（如果有需要，默认为5000）
EXPOSE 5000

# 启动Flask应用程序（假设入口文件为main.py）
CMD ["flask", "run"]
