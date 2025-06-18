import { useEffect, useState } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

const API_URL = "http://43.201.168.127:3000/temperatures";

function TemperatureChart() {
  const [data, setData] = useState([]);
  const [baseTemp, setBaseTemp] = useState(null);

  // 초기 로컬스토리지 데이터 불러오기
  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem("graph_data"));
    if (saved) setData(saved);
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(API_URL);
        if (res.status === 200) {
          const base = res.data.temperature ?? 25.0;
          const simulated = parseFloat((base + Math.random() * 20 - 10).toFixed(2));
          setBaseTemp(base);

          setData((prev) => {
            const updated = [...prev, simulated];
            localStorage.setItem("graph_data", JSON.stringify(updated));
            return updated;
          });
        }
      } catch (error) {
        console.error("API 오류:", error);
      }
    };

    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const chartData = {
    labels: data.map((_, idx) => idx + 1),
    datasets: [
      {
        label: "Simulated Temperature (°C)",
        data,
        fill: false,
        borderColor: "#3b82f6",
        backgroundColor: "#3b82f6",
        tension: 0.3,
      },
    ],
  };

  return (
    <div style={{ width: "100%", maxWidth: 900, margin: "0 auto", padding: "20px" }}>
      <h2>📊 실시간 온도 그래프 (±10 오차 포함)</h2>
      <Line data={chartData} />
      {baseTemp !== null && (
        <p style={{ marginTop: 10 }}>
          🧪 기준 온도: <strong>{baseTemp}℃</strong> | 누적:{" "}
          <strong>{data.length}개</strong>
        </p>
      )}
      <button
        onClick={() => {
          localStorage.removeItem("graph_data");
          setData([]);
        }}
        style={{ marginTop: 10, padding: "5px 10px" }}
      >
        초기화
      </button>
    </div>
  );
}

export default TemperatureChart
