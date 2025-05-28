import os, json, threading
import pika, redis, dotenv

dotenv.load_dotenv()
queue    = os.getenv("QUEUE")
r        = redis.Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
CACHE_KEY = "events:list"

def callback(ch, method, properties, body):
    msg = json.loads(body.decode())
    # guarda na mesma lista de eventos
    r.rpush(CACHE_KEY, json.dumps({"source":"PHP-logistics", **msg}))
    r.expire(CACHE_KEY, int(os.getenv("CACHE_TTL", 60)))

def start_consumer_thread():
    def _run():
        connection = pika.BlockingConnection(pika.URLParameters(os.getenv("RABBITMQ_URL")))
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_consume(queue, callback, auto_ack=True)
        channel.start_consuming()
    threading.Thread(target=_run, daemon=True).start()
