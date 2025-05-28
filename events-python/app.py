import os, json
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from redis import Redis
from consumer import start_consumer_thread

load_dotenv()
redis = Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
CACHE_KEY = "events:list"
app = Flask(__name__)

@app.post("/event")
def add_event():
    event = request.json or {}
    events = redis.lrange(CACHE_KEY, 0, -1)
    events.append(json.dumps(event))
    redis.delete(CACHE_KEY)
    redis.rpush(CACHE_KEY, *events)
    redis.expire(CACHE_KEY, int(os.getenv("CACHE_TTL", 60)))
    return {"saved": event}, 201

@app.get("/events")
def get_events():
    events = redis.lrange(CACHE_KEY, 0, -1)
    return jsonify([json.loads(e) for e in events])

if __name__ == "__main__":
    start_consumer_thread()               # inicia o consumidor RabbitMQ em background
    app.run(port=int(os.getenv("PORT", 5000)), host="0.0.0.0")
