// server.js
const express = require('express');
const cors = require('cors');
const app = express();

let latestData = null;
let clients = [];

app.use(cors());
app.use(express.json());

app.post('/temperature-data', (req, res) => {
  const { temperature, humidity, timestamp } = req.body;

  if (
    typeof temperature !== 'number' ||
    typeof humidity !== 'number'
  ) {
    return res.status(400).json({ message: 'Invalid data' });
  }

  latestData = { temperature, humidity, timestamp };

  // SSE로 모든 클라이언트에게 전달
  clients.forEach(client => {
    client.write(`data: ${JSON.stringify(latestData)}\n\n`);
  });

  res.json({ message: 'Data received' });
});

app.get('/temperature-stream', (req, res) => {
  res.set({
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
  });
  res.flushHeaders();

  if (latestData) {
    res.write(`data: ${JSON.stringify(latestData)}\n\n`);
  } else {
    res.write(`data: {"message": "No data"}\n\n`);
  }

  clients.push(res);

  req.on('close', () => {
    clients = clients.filter(c => c !== res);
  });
});

app.listen(3000, () => {
  console.log('Server running on http://43.201.168.127:3000');
});
