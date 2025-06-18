# import threading
# import time
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse
# from motor.motor_asyncio import AsyncIOMotorClient
# from datetime import datetime, timedelta
# import asyncio
# import json
# import serial
# from pymongo import DESCENDING

# app = FastAPI()

# # MongoDB 연결
# client = AsyncIOMotorClient("mongodb://admin:admin123@43.201.168.127:27017/?authSource=admin")
# db = client["sensor_db"]
# collection = db["temperature_collection"]

# # CORS 설정
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# temperature_buffer = []
# buffer_start_time = datetime.utcnow()

# SERIAL_PORT = "COM3"  # 환경에 맞게 바꾸세요 (예: 리눅스 /dev/ttyUSB0)
# BAUD_RATE = 115200

# # 시리얼 포트 오픈
# try:
#     ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
# except Exception as e:
#     print(f"❌ 시리얼 포트 열기 실패: {e}")
#     ser = None

# # 시리얼 데이터 읽기 (별도 스레드에서 동작)
# def read_serial_sync():
#     global temperature_buffer
#     if ser is None:
#         print("❌ 시리얼 포트가 없습니다.")
#         return

#     while True:
#         try:
#             line = ser.readline().decode('utf-8').strip()
#             if line.startswith("TEMP:"):
#                 parts = line.replace("TEMP:", "").split(",HUM:")
#                 if len(parts) == 2:
#                     temp = float(parts[0])
#                     humidity = float(parts[1])
#                     print(f"📡 읽음 → Temp: {temp}°C, Humidity: {humidity}%")
#                     temperature_buffer.append(temp)
#         except Exception as e:
#             print("❌ 시리얼 읽기 실패:", e)
#         time.sleep(1)

# # 1시간마다 평균값 MongoDB에 저장
# async def save_avg():
#     global temperature_buffer, buffer_start_time
#     while True:
#         await asyncio.sleep(3600)  # 1시간 대기

#         if temperature_buffer:
#             avg_temp = round(sum(temperature_buffer) / len(temperature_buffer), 2)
#             data = {
#                 "timestamp": datetime.utcnow(),
#                 "avg_temperature": avg_temp
#             }
#             try:
#                 await collection.insert_one(data)
#                 print(f"✅ 평균 저장됨: {data}")
#             except Exception as e:
#                 print(f"❌ 저장 실패: {e}")
#         else:
#             print("ℹ️ 저장할 데이터가 없음")

#         temperature_buffer = []
#         buffer_start_time = datetime.utcnow()

# # 실시간 온도 스트림 (SSE)
# @app.get("/temperature-stream")
# async def temperature_stream():
#     async def event_generator():
#         while True:
#             if temperature_buffer:
#                 latest_temp = temperature_buffer[-1]
#                 data = {
#                     "timestamp": datetime.utcnow().isoformat(),
#                     "temperature": latest_temp
#                 }
#                 yield f"data: {json.dumps(data)}\n\n"
#             else:
#                 yield f"data: {json.dumps({'message': 'No data'})}\n\n"
#             await asyncio.sleep(5)
#     return StreamingResponse(event_generator(), media_type="text/event-stream")

# # 버퍼 상태 확인 API
# @app.get("/buffer-status")
# async def buffer_status():
#     return {
#         "current_count": len(temperature_buffer),
#         "buffer_start": buffer_start_time.isoformat(),
#         "latest_values": temperature_buffer[-5:]
#     }

# # 24시간 이내 시간별 평균값 반환 API
# @app.get("/hourly-averages")
# async def get_hourly_averages():
#     try:
#         since = datetime.utcnow() - timedelta(hours=24)
#         cursor = collection.find({"timestamp": {"$gte": since}}).sort("timestamp", DESCENDING)
#         results = await cursor.to_list(length=1000)

#         hourly_map = {}
#         for doc in results:
#             timestamp = doc["timestamp"]
#             hour_key = timestamp.replace(minute=0, second=0, microsecond=0)
#             hourly_map.setdefault(hour_key, []).append(doc["avg_temperature"])

#         hourly_averages = [
#             {
#                 "timestamp": hour.isoformat(),
#                 "avg_temperature": round(sum(temps) / len(temps), 2)
#             }
#             for hour, temps in sorted(hourly_map.items())
#         ]
#         return hourly_averages

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # 서버 시작 시 MongoDB 연결 테스트, 시리얼 읽기 스레드 시작, 평균 저장 비동기 태스크 실행
# @app.on_event("startup")
# async def startup_event():
#     try:
#         await client.admin.command('ping')
#         print("✅ MongoDB 연결 성공")
#     except Exception as e:
#         print(f"❌ MongoDB 연결 실패: {e}")

#     thread = threading.Thread(target=read_serial_sync, daemon=True)
#     thread.start()

#     asyncio.create_task(save_avg())


from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi_utils.tasks import repeat_every
import statistics
from datetime import datetime
from zoneinfo import ZoneInfo  # ✅ Python 3.9 이상에서 사용 가능

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB 연결
client = AsyncIOMotorClient("mongodb://admin:admin123@43.201.168.127:27017/?authSource=admin")
db = client["sensor_db"]
collection = db["temperature_collection"]

# 메모리에 1시간 동안 수집할 센서 데이터
hourly_data = []

KST = ZoneInfo("Asia/Seoul")  # ✅ 한국 시간대 설정

@app.get("/")
def root():
    return {"message": "Server running"}

@app.post("/receive-data")
async def receive_data(request: Request):
    data = await request.json()
    temperature = float(data.get("temperature"))
    humidity = float(data.get("humidity"))

    print(f"✅ 온도 !! 센서 !!: Temp={temperature}, Humidity={humidity}")

    hourly_data.append({
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": datetime.now(KST)  # ✅ 한국시간으로 저장
    })

    return {"status": "success"}

@app.get("/get-data")
def get_data():
    return {"data": hourly_data[-20:]}  # 최근 20개만 반환

# ⏲️ 1시간마다 평균 내어 MongoDB에 저장하는 백그라운드 작업
@app.on_event("startup")
@repeat_every(seconds=3600)
async def store_hourly_average():
    if not hourly_data:
        return

    avg_temp = statistics.mean([d["temperature"] for d in hourly_data])
    avg_humidity = statistics.mean([d["humidity"] for d in hourly_data])
    now = datetime.now(KST)  # ✅ 한국시간 기준으로 기록

    document = {
        "average_temperature": avg_temp,
        "average_humidity": avg_humidity,
        "timestamp": now
    }

    await collection.insert_one(document)
    print(f"📝 MongoDB에 저장됨: {document}")

    hourly_data.clear()
