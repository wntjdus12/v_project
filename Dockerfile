# 1. Python 베이스 이미지
FROM python:3.10-slim

# 2. 작업 디렉토리
WORKDIR /app

# 3. 필요한 파일 복사
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. FastAPI 코드 복사
COPY . .

# 5. uvicorn으로 FastAPI 실행
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3000"]
