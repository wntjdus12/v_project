from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import asyncio

app = FastAPI()

client = AsyncIOMotorClient("mongodb://3.36.70.226:27017")
db = client["sensor_db"]
collection = db["temperature_avg"]

temperature_buffer = []
buffer_start_time = datetime.utcnow()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

temperature_data = []

# @app.get("/get-sensor")
# async def get_sensor(temperature: float):
#     base_temp = res.json().get("temperature", 25.0)
#     simulated_temp = round(base_temp + random.uniform(-10, 10), 2)
#     temperature_data.append(simulated_temp)
#     return {"message": "온도 데이터 수신 완료", "received_temperature": simulated_temp}

@app.get("/get-sensor")
async def get_sensor(temperature: float):
    simulated_temp = round(temperature + random.uniform(-10, 10), 2)
    temperature_data.append(simulated_temp)
    return {"message": "온도 데이터 수신 완료", "received_temperature": simulated_temp}

# async def save_avg_temp_hourly():
#     global temperature_buffer, buffer_start_time
#     while True:
#         await asyncio.sleep(3600)  # 1시간 대기
#         if temperature_buffer:
#             avg_temp = sum(temperature_buffer) / len(temperature_buffer)
#             data = {
#                 "timestamp": buffer_start_time,
#                 "avg_temperature": round(avg_temp, 2)
#             }
#             await collection.insert_one(data)
#             temperature_buffer = []
#             buffer_start_time = datetime.utcnow()

@app.get("/temperatures")
async def get_temperatures():
    return {"temperatures": temperature_data}

# @app.post("/save-temperature/")
# async def save_temperature(temp: float):
#     global temperature_buffer, buffer_start_time
    
#     temperature_buffer.append(temp)
#     now = datetime.utcnow()

#     if now - buffer_start_time >= timedelta(hours=1):
#         avg_temp = sum(temperature_buffer) / len(temperature_buffer)
#         data = {
#             "timestamp": buffer_start_time,
#             "avg_temperature": round(avg_temp, 2)
#         }
#         await collection.insert_one(data)
#         temperature_buffer = []
#         buffer_start_time = now

#     return {"message": "온도값 수신 및 저장 준비 완료"}

