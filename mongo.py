import asyncio
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB 클라이언트 설정
client = AsyncIOMotorClient("mongodb://admin:admin123@43.201.168.127:27017/?authSource=admin")
db = client["sensor_db"]
collection = db["Temperature_Humidity_Data"]

# CSV 파일 경로
csv_file_path = "MongoDB__________KST_.csv"

async def import_csv_to_mongo():
    # CSV 읽기
    df = pd.read_csv(csv_file_path)

    # 각 행을 dict로 변환
    documents = df.to_dict(orient="records")

    # 기존 데이터 제거 (선택)
    await collection.delete_many({})

    # MongoDB에 데이터 삽입
    if documents:
        result = await collection.insert_many(documents)
        print(f"{len(result.inserted_ids)}개의 문서가 성공적으로 삽입되었습니다.")
    else:
        print("삽입할 문서가 없습니다.")

# 실행
if __name__ == "__main__":
    asyncio.run(import_csv_to_mongo())
