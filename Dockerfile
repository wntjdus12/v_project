FROM python:3.10

WORKDIR /app

# 의존성 먼저 복사 (캐시 유지를 위함)
COPY requirements.txt ./
RUN pip install -r requirements.txt

# 이후 소스 복사
COPY . .

EXPOSE 5000
CMD ["python", "app.py"]