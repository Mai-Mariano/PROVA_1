import os, json
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from redis import Redis
from consumer import start_consumer_thread

load_dotenv()

# --- Config --------------------------------------------------------
redis      = Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
CACHE_KEY  = "events:list"
CACHE_TTL  = int(os.getenv("CACHE_TTL", 60))
PORT       = int(os.getenv("PORT", 5000))

app = Flask(__name__)

# --- Rotas ---------------------------------------------------------
@app.post("/event")
def add_event():
    event = request.json or {}
    # salva diretamente
    redis.rpush(CACHE_KEY, json.dumps(event))
    redis.expire(CACHE_KEY, CACHE_TTL)
    return {"saved": event}, 201

@app.get("/events")
def get_events():
    events = redis.lrange(CACHE_KEY, 0, -1)
    return jsonify([json.loads(e) for e in events])

# --- Main ----------------------------------------------------------
if __name__ == "__main__":
    start_consumer_thread()         # consumidor RabbitMQ em background
    app.run(host="0.0.0.0", port=PORT)
