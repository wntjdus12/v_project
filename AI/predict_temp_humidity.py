from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from datetime import datetime, timedelta

start_date = datetime.now()

llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.3, max_tokens=1024)

prompt = PromptTemplate(
    input_variables=["date", "observed_11", "peak_temp"],
    template="""
You are a professional weather forecaster.

Today is {date} in Seoul. By observation:
- At 11:00 → temperature was **{observed_11}°C**
- At 15:00 → peak temperature reached **{peak_temp}°C**, with humidity around 48%

Use these observed data points as anchors.

Hourly temperature/humidity pattern should follow:
- 🌅 06:00 → around **22°C**, humidity ~70%
- 🕚 11:00 → exactly **{observed_11}°C**
- 🌞 15:00 → peak at **{peak_temp}°C**
- 🌇 After 18:00 → gradual cooling

Constraints:
- Temperature: 20°C–36°C
- Humidity: 48%–75%

Return exactly 24 hourly entries like this:
{date} 00:00 → Temperature: XX.X°C, Humidity: YY%
...
{date} 23:00 → ...
"""
)

# 예시 값
observed_11 = 29.5
peak_temp = 34.7

forecast_all_days = []
for i in range(7):
    target_date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
    result = (prompt | llm).invoke({
        "date": target_date,
        "observed_11": observed_11,
        "peak_temp": peak_temp
    })
    forecast_all_days.append(result)

print("\n\n".join(forecast_all_days))
