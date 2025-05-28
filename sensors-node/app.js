require('dotenv').config();
const express = require('express');
const Redis = require('ioredis');
const axios = require('axios');

const redis = new Redis(process.env.REDIS_URL);
const app = express();
app.use(express.json());

function simulateSensor() {
  return {
    temperature: (20 + Math.random() * 40).toFixed(2), // 20-60 °C
    pressure: (100 + Math.random() * 50).toFixed(2)    // 100-150 bar
  };
}

app.get('/sensor-data', async (_, res) => {
  const cacheKey = 'sensor:data';
  let data = await redis.get(cacheKey);

  if (!data) {
    data = JSON.stringify(simulateSensor());
    await redis.set(cacheKey, data, 'EX', process.env.CACHE_TTL);
  }
  res.json(JSON.parse(data));
});

app.post('/alert', async (req, res) => {
  try {
    await axios.post(process.env.PYTHON_API, req.body);
    res.status(201).json({ status: 'forwarded to Python service' });
  } catch (e) {
    res.status(502).json({ error: 'Python API unavailable', detail: e.message });
  }
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Sensor API listening on ${port}`));
